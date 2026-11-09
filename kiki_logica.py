"""
kiki_logica.py - Lógica pura de Kiki Pay (SIN Streamlit).

Todo lo que se puede probar sin interfaz vive aquí: validación de movimientos,
totales, cambio, metas de ahorro, generador de retos, base de conocimientos de
Kiki, respaldo y restauración de datos.

Los datos que manejan estas funciones son FICTICIOS o de práctica.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from datetime import date, datetime, timedelta

VERSION_RESPALDO = 1
MAX_CANTIDAD = 10_000_000
MAX_DESCRIPCION = 120
MAX_REGISTROS = 5000

# (tipo, valor) de mayor a menor. Solo pesos enteros en los ejercicios.
DENOMINACIONES = [
    ("billete", 200), ("billete", 100), ("billete", 50), ("billete", 20),
    ("moneda", 10), ("moneda", 5), ("moneda", 2), ("moneda", 1),
]

CATEGORIAS = {
    "Ingreso": ["Apoyo familiar", "Dinero para gastos personales", "Ingresos laborales",
                "Emprendimiento", "Pensión o prestación", "Otros ingresos"],
    "Gasto": ["Alimentación", "Transporte", "Ropa", "Entretenimiento",
              "Educación", "Salud", "Compras personales", "Otros"],
}

TAMANOS = {"Pequeña": 16, "Mediana": 18, "Grande": 21, "Muy grande": 24}
MODOS = ["Pictogramas", "Imagen y número", "Solo números"]

PREFS_DEFAULT = {
    "nombre": "", "tamano": "Mediana", "contraste": False, "pistas": True,
    "reducir": False, "pictos": True, "modo": "Imagen y número", "dificultad": 1,
}
PROGRESO_DEFAULT = {
    "dinero_ok": 0, "dinero_total": 0, "suma_ok": 0, "suma_total": 0,
    "compras": 0, "retos_ok": 0, "retos_total": 0,
}

# nombre -> (emoji, precio, categoría de gasto)
PRODUCTOS = {
    "Manzana": ("🍎", 12, "Alimentación"),
    "Leche": ("🥛", 24, "Alimentación"),
    "Pan": ("🍞", 18, "Alimentación"),
    "Cuaderno": ("📒", 35, "Educación"),
    "Colores": ("🖍️", 42, "Educación"),
    "Jabón": ("🧼", 16, "Compras personales"),
    "Boleto de camión": ("🚌", 9, "Transporte"),
    "Playera": ("👕", 120, "Ropa"),
}


# ----------------------------------------------------------------- utilidades
def _numero(valor) -> float:
    """Convierte a float finito o lanza ValueError/TypeError."""
    if isinstance(valor, bool):
        raise ValueError("booleano no es cantidad")
    n = float(valor)
    if not math.isfinite(n):
        raise ValueError("cantidad no finita")
    return n


def formato_dinero(valor) -> str:
    try:
        v = _numero(valor)
    except (TypeError, ValueError):
        return "$0"
    if v == int(v):
        return f"${int(v):,}"
    return f"${v:,.2f}"


def _fecha_iso(valor):
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor.strip()).isoformat()
        except ValueError:
            return None
    return None


# ------------------------------------------------------ ingresos y gastos
def crear_movimiento(tipo, cantidad, categoria, descripcion, fecha, id_):
    """Valida y crea un movimiento. Devuelve (movimiento, None) o (None, error)."""
    if tipo not in CATEGORIAS:
        return None, "Elige si es un ingreso o un gasto."
    try:
        cant = round(_numero(cantidad), 2)
    except (TypeError, ValueError):
        return None, "Escribe una cantidad válida."
    if cant <= 0:
        return None, "Escribe una cantidad mayor que cero."
    if cant > MAX_CANTIDAD:
        return None, "Esa cantidad es muy grande para practicar. Prueba con una menor."
    if categoria not in CATEGORIAS[tipo]:
        return None, "Elige una categoría de la lista."
    f = _fecha_iso(fecha)
    if f is None:
        return None, "La fecha no es válida."
    desc = (descripcion or "").strip()[:MAX_DESCRIPCION] or categoria
    return {"id": int(id_), "fecha": f, "tipo": tipo, "categoria": categoria,
            "descripcion": desc, "cantidad": cant}, None


def totales(movimientos):
    """(ingresos, gastos, saldo). Usa SIEMPRE las claves en minúscula."""
    ingresos = sum(m["cantidad"] for m in movimientos if m.get("tipo") == "Ingreso")
    gastos = sum(m["cantidad"] for m in movimientos if m.get("tipo") == "Gasto")
    return round(ingresos, 2), round(gastos, 2), round(ingresos - gastos, 2)


def gastos_por_categoria(movimientos) -> dict:
    acc: dict = {}
    for m in movimientos:
        if m.get("tipo") == "Gasto":
            acc[m["categoria"]] = round(acc.get(m["categoria"], 0) + m["cantidad"], 2)
    return dict(sorted(acc.items(), key=lambda kv: -kv[1]))


# ------------------------------------------------------------ compras y cambio
def calcular_cambio(precio, pago) -> dict:
    precio, pago = _numero(precio), _numero(pago)
    if pago >= precio:
        return {"suficiente": True, "cambio": round(pago - precio, 2), "falta": 0}
    return {"suficiente": False, "cambio": 0, "falta": round(precio - pago, 2)}


def desglose_cambio(monto):
    """Piezas (tipo, valor, cantidad) que forman un monto entero de pesos."""
    resto = int(_numero(monto))
    piezas = []
    for tipo, valor in DENOMINACIONES:
        n, resto = divmod(resto, valor)
        if n:
            piezas.append((tipo, valor, n))
    return piezas


# ------------------------------------------------------------ piezas de dinero
def valores_expandidos(items):
    return [valor for _t, valor, n in items for _ in range(n)]


def describir_piezas(items) -> str:
    partes = []
    for tipo, valor, n in items:
        if tipo == "billete":
            nombre = "billete" if n == 1 else "billetes"
        else:
            nombre = "moneda" if n == 1 else "monedas"
        partes.append(f"{n} {nombre} de ${valor}")
    return ", ".join(partes)


def expresion_suma(items) -> str:
    return " + ".join(str(v) for v in valores_expandidos(items))


def conteo_progresivo(items) -> str:
    acumulado, pasos = 0, []
    for v in valores_expandidos(items):
        acumulado += v
        pasos.append(f"${acumulado}")
    return " → ".join(pasos)


def generar_ejercicio_dinero(nivel, rng) -> dict:
    nivel = nivel if nivel in (1, 2, 3) else 1
    if nivel == 1:
        pool = [("moneda", 1), ("moneda", 2), ("moneda", 5), ("moneda", 10),
                ("billete", 20), ("billete", 50)]
        tipo, valor = rng.choice(pool)
        items = [(tipo, valor, rng.randint(1, 2))]
    else:
        k, maximo = (2, 2) if nivel == 2 else (3, 3)
        elegidas = rng.sample(DENOMINACIONES, k)
        items = [(t, v, rng.randint(1, maximo)) for t, v in elegidas]
    items.sort(key=lambda x: -x[1])
    total = sum(v * n for _t, v, n in items)
    paso = min(v for _t, v, _n in items)
    candidatos = []
    for d in (paso, -paso, 2 * paso, -2 * paso, 5, -5, 10):
        if total + d > 0 and total + d != total and total + d not in candidatos:
            candidatos.append(total + d)
    rng.shuffle(candidatos)
    cuantas = 3 if nivel == 1 else 4
    opciones = sorted([total] + candidatos[:cuantas - 1])
    return {"nivel": nivel, "items": items, "total": total, "opciones": opciones}


# ---------------------------------------------------------------- metas de ahorro
def crear_meta(nombre, objetivo, ahorrado, id_):
    nombre = (nombre or "").strip()
    if not nombre:
        return None, "Escribe el nombre de tu meta."
    try:
        obj, ah = round(_numero(objetivo), 2), round(_numero(ahorrado), 2)
    except (TypeError, ValueError):
        return None, "Escribe cantidades válidas."
    if obj <= 0:
        return None, "La cantidad que quieres juntar debe ser mayor que cero."
    if ah < 0:
        return None, "Lo que llevas ahorrado no puede ser negativo."
    if obj > MAX_CANTIDAD or ah > MAX_CANTIDAD:
        return None, "Esa cantidad es muy grande para practicar."
    return {"id": int(id_), "nombre": nombre[:60], "objetivo": obj, "ahorrado": ah}, None


def agregar_ahorro(meta, cantidad):
    """Devuelve (meta_nueva, None) o (None, error). No modifica la original."""
    try:
        cant = round(_numero(cantidad), 2)
    except (TypeError, ValueError):
        return None, "Escribe una cantidad válida."
    if cant <= 0:
        return None, "Escribe una cantidad mayor que cero."
    if cant > MAX_CANTIDAD:
        return None, "Esa cantidad es muy grande para practicar."
    nueva = dict(meta)
    nueva["ahorrado"] = round(meta["ahorrado"] + cant, 2)
    return nueva, None


def progreso_meta(meta) -> float:
    if meta["objetivo"] <= 0:
        return 0.0
    return max(0.0, min(meta["ahorrado"] / meta["objetivo"], 1.0))


def falta_meta(meta):
    return round(max(meta["objetivo"] - meta["ahorrado"], 0), 2)


def mensaje_meta(meta) -> str:
    p = progreso_meta(meta)
    if p >= 1:
        return "¡Meta alcanzada! Lo lograste poco a poco. 🎉"
    if p >= 0.75:
        return "¡Ya casi! Estás muy cerca de tu meta."
    if p >= 0.5:
        return "¡Vas más de la mitad! Sigue a tu ritmo."
    if p > 0:
        return "¡Buen comienzo! Cada cantidad cuenta."
    return "Cuando agregues tu primera cantidad, empezará a avanzar la barra."


def semanas_para_meta(falta, por_semana):
    """Semanas necesarias (entero) o None si no se puede calcular."""
    try:
        falta, por_semana = _numero(falta), _numero(por_semana)
    except (TypeError, ValueError):
        return None
    if falta <= 0:
        return 0
    if por_semana <= 0:
        return None
    return math.ceil(falta / por_semana)


# ---------------------------------------------------------------------- retos
def _opciones_numericas(correcta, paso, rng, cantidad=3):
    candidatos = [correcta + k * paso for k in (1, -1, 2, -2, 3)
                  if correcta + k * paso > 0 and k != 0]
    rng.shuffle(candidatos)
    return sorted([correcta] + candidatos[:cantidad - 1])


def _reto_numerico(pregunta, correcta, paso, explicacion, pista, nivel, tipo, rng):
    valores = _opciones_numericas(correcta, paso, rng)
    return {"nivel": nivel, "tipo": tipo, "pregunta": pregunta,
            "opciones": [formato_dinero(v) for v in valores],
            "correcta": formato_dinero(correcta),
            "explicacion": explicacion, "pista": pista}


TIPOS_RETO = {
    1: ["resta", "menor", "ahorro"],
    2: ["resta", "ahorro", "menor", "gastar_mas"],
    3: ["resta", "ahorro", "menor", "gastar_mas", "semana"],
}


def generar_reto(nivel, rng) -> dict:
    nivel = nivel if nivel in (1, 2, 3) else 1
    tipo = rng.choice(TIPOS_RETO[nivel])
    if tipo in ("resta", "ahorro"):
        total = rng.choice({1: [20, 50, 100], 2: list(range(50, 201, 10)),
                            3: list(range(100, 501, 10))}[nivel])
        parte = 5 * rng.randint(1, (total - 5) // 5 if nivel > 1 else min(6, (total - 5) // 5))
        resto = total - parte
        paso = 10 if nivel == 1 else 5
        if tipo == "resta":
            return _reto_numerico(
                f"Tienes {formato_dinero(total)} y compras algo de {formato_dinero(parte)}. ¿Cuánto queda?",
                resto, paso, f"{total} − {parte} = {resto}. Quedan {formato_dinero(resto)}.",
                "Para saber cuánto queda, resta: lo que tenías menos lo que gastaste.",
                nivel, tipo, rng)
        return _reto_numerico(
            f"Recibes {formato_dinero(total)} y decides ahorrar {formato_dinero(parte)}. ¿Cuánto puedes gastar?",
            resto, paso, f"{total} − {parte} = {resto}. Puedes gastar {formato_dinero(resto)}.",
            "Lo que puedes gastar es lo que recibes menos lo que ahorras.",
            nivel, tipo, rng)
    if tipo == "menor":
        nombres = list(PRODUCTOS)
        while True:
            a, b = rng.sample(nombres, 2)
            if PRODUCTOS[a][1] != PRODUCTOS[b][1]:
                break
        ea, pa, _ = PRODUCTOS[a]
        eb, pb, _ = PRODUCTOS[b]
        barato = a if pa < pb else b
        etiqueta = lambda n: f"{PRODUCTOS[n][0]} {n}"  # noqa: E731
        return {"nivel": nivel, "tipo": tipo,
                "pregunta": f"{etiqueta(a)} cuesta {formato_dinero(pa)} y {etiqueta(b)} cuesta {formato_dinero(pb)}. ¿Qué producto cuesta menos?",
                "opciones": [etiqueta(a), etiqueta(b)], "correcta": etiqueta(barato),
                "explicacion": f"{formato_dinero(min(pa, pb))} es menos que {formato_dinero(max(pa, pb))}, así que {etiqueta(barato)} cuesta menos.",
                "pista": "Compara los dos números: el menor es el más barato."}
    if tipo == "gastar_mas":
        recibe = rng.choice(range(20, 101, 10))
        gasto = recibe + 5 * rng.randint(2, 8)
        dif = gasto - recibe
        opciones = [f"Me faltan {formato_dinero(dif)}", f"Me sobran {formato_dinero(dif)}", "Me alcanza justo"]
        rng.shuffle(opciones)
        return {"nivel": nivel, "tipo": tipo,
                "pregunta": f"Recibes {formato_dinero(recibe)} y quieres gastar {formato_dinero(gasto)}. ¿Qué sucede?",
                "opciones": opciones, "correcta": f"Me faltan {formato_dinero(dif)}",
                "explicacion": f"Si gastas más de lo que recibes, te falta dinero: {gasto} − {recibe} = {dif}. Puedes elegir algo más barato o ahorrar antes.",
                "pista": "Compara lo que recibes con lo que quieres gastar."}
    # semana
    semanas = rng.choice([2, 4, 5, 10])
    por_semana = 5 * rng.randint(1, 10)
    meta = semanas * por_semana
    return _reto_numerico(
        f"Quieres juntar {formato_dinero(meta)} en {semanas} semanas. ¿Cuánto debes ahorrar cada semana?",
        por_semana, 5, f"{meta} ÷ {semanas} = {por_semana}. Ahorrarías {formato_dinero(por_semana)} cada semana.",
        "Reparte la meta entre las semanas: divide.", nivel, tipo, rng)


# --------------------------------------------------------- progreso / habilidades
def habilidades(progreso) -> list:
    """Resumen descriptivo y respetuoso; nunca etiqueta como 'malo'."""
    filas = []
    for nombre, ok, total in (
        ("Reconocer monedas y billetes", progreso.get("dinero_ok", 0), progreso.get("dinero_total", 0)),
        ("Sumar y restar", progreso.get("suma_ok", 0), progreso.get("suma_total", 0)),
        ("Retos de situaciones cotidianas", progreso.get("retos_ok", 0), progreso.get("retos_total", 0)),
    ):
        if total == 0:
            estado = "Aún sin practicar"
        elif total < 5:
            estado = "Empezando"
        elif ok / total >= 0.8:
            estado = "Con mucha seguridad"
        elif ok / total >= 0.5:
            estado = "Avanzando"
        else:
            estado = "En práctica (puede ayudar más acompañamiento)"
        filas.append({"Habilidad": nombre, "Aciertos": ok, "Intentos": total, "Estado": estado})
    filas.append({"Habilidad": "Compras practicadas", "Aciertos": progreso.get("compras", 0),
                  "Intentos": progreso.get("compras", 0), "Estado": "Registro de práctica"})
    return filas


# -------------------------------------------------------------- Kiki (base local)
def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


BASE_KIKI = [
    {"id": "dinero", "titulo": "¿Qué es el dinero?", "claves": ["dinero", "moneda", "billete"],
     "texto": "El dinero sirve para intercambiar cosas: con él pagamos lo que necesitamos o queremos. Existen monedas y billetes, y cada uno tiene un valor escrito."},
    {"id": "ingreso", "titulo": "¿Qué es un ingreso?", "claves": ["ingreso", "sueldo", "recibo dinero", "pension"],
     "texto": "Un ingreso es el dinero que recibes: apoyo familiar, un pago por trabajo, una pensión u otro dinero. Registrar tus ingresos te ayuda a saber cuánto tienes."},
    {"id": "gasto", "titulo": "¿Qué es un gasto?", "claves": ["gasto", "gastar"],
     "texto": "Un gasto es el dinero que usas para pagar algo: comida, transporte, ropa o diversión. Anotar tus gastos te ayuda a ver en qué se va el dinero."},
    {"id": "ahorro", "titulo": "¿Qué es ahorrar?", "claves": ["ahorr", "guardar dinero"],
     "texto": "Ahorrar es guardar una parte del dinero para usarla después. Puedes elegir una meta y avanzar poco a poco; cada cantidad cuenta."},
    {"id": "meta", "titulo": "¿Cómo pongo una meta?", "claves": ["meta"],
     "texto": "Elige algo que quieras lograr, escribe cuánto cuesta y cuánto llevas. Divide lo que falta entre las semanas que quieras esperar y verás cuánto guardar cada semana."},
    {"id": "presupuesto", "titulo": "¿Qué es un presupuesto?", "claves": ["presupuesto", "organizar"],
     "texto": "Un presupuesto es un plan: decides cuánto dinero vas a usar en cada cosa antes de gastarlo, y apartas una parte para ahorrar."},
    {"id": "necesidad", "titulo": "Necesidades y deseos", "claves": ["necesidad", "deseo"],
     "texto": "Una necesidad es algo importante para vivir o estar bien, como comida, agua o medicinas. Un deseo es algo que te gustaría tener, pero puede esperar."},
    {"id": "cambio", "titulo": "¿Qué es el cambio?", "claves": ["cambio", "vuelto"],
     "texto": "El cambio es el dinero que te regresan cuando entregas más de lo que cuesta algo. Se calcula restando: dinero entregado menos precio."},
    {"id": "comparar", "titulo": "Comparar precios", "claves": ["comparar", "precio"],
     "texto": "Para comparar, mira cuánto cuesta cada opción y qué te ofrece. A veces lo más barato es suficiente y a veces conviene esperar para elegir mejor."},
    {"id": "compra", "titulo": "Comprar con calma", "claves": ["comprar", "compra responsable"],
     "texto": "Antes de comprar, pregúntate: ¿lo necesito?, ¿me alcanza?, ¿puedo esperar? Revisar tu dinero disponible te ayuda a decidir con tranquilidad."},
    {"id": "cuenta", "titulo": "¿Qué es una cuenta bancaria?", "claves": ["cuenta", "banco", "bancari"],
     "texto": "Una cuenta bancaria es un lugar seguro, dentro de un banco, donde se guarda dinero. Tiene un saldo, que es lo que hay disponible, y registra lo que entra y lo que sale."},
    {"id": "saldo", "titulo": "¿Qué es el saldo?", "claves": ["saldo"],
     "texto": "El saldo es el dinero que tienes disponible en este momento. Sube cuando recibes dinero y baja cuando pagas."},
    {"id": "debito", "titulo": "¿Qué es una tarjeta de débito?", "claves": ["debito", "tarjeta de debito", "tarjeta"],
     "texto": "Una tarjeta de débito usa el dinero que ya tienes en tu cuenta. Si pagas con ella, ese dinero sale de tu cuenta. Tu NIP es secreto y no se comparte."},
    {"id": "transferencia", "titulo": "¿Qué es una transferencia?", "claves": ["transferencia", "transferir", "spei"],
     "texto": "Una transferencia es enviar dinero de una cuenta a otra sin usar billetes. Antes de enviarla se revisa con mucho cuidado a quién se la mandas."},
    {"id": "pagos", "titulo": "Pagos digitales", "claves": ["pago digital", "pagos digitales", "aplicacion", "codigo qr"],
     "texto": "Un pago digital se hace con el celular o una tarjeta, sin entregar billetes. Es importante revisar el monto antes de confirmar."},
    {"id": "comision", "titulo": "¿Qué es una comisión?", "claves": ["comision"],
     "texto": "Una comisión es un cobro por usar un servicio financiero, por ejemplo retirar dinero en ciertos cajeros. Conviene preguntar qué comisiones existen antes de usar un servicio."},
    {"id": "seguridad", "titulo": "Cómo cuidar mi cuenta", "claves": ["seguridad", "proteger", "fraude", "estafa", "engano", "contrasena", "nip", "clabe"],
     "texto": "Nunca compartas tu NIP, contraseñas ni códigos que te lleguen por mensaje. Un banco de verdad no te los pide por llamada o chat. Si dudas, para y pregunta a una persona de confianza."},
    {"id": "credito", "titulo": "¿Qué es un crédito?", "claves": ["credito", "prestamo", "prestar", "pedir dinero prestado"],
     "texto": "Un crédito es dinero que te presta una institución y que debes devolver, normalmente con intereses y en fechas acordadas. No es dinero extra: es dinero que hay que pagar. Antes de pedir uno, conviene entender todo lo que implica."},
    {"id": "deuda", "titulo": "¿Qué es una deuda?", "claves": ["deuda", "deber"],
     "texto": "Una deuda es el dinero que debes pagar porque lo pediste prestado o porque compraste a crédito. Mientras no la pagues completa, sigue existiendo."},
    {"id": "interes", "titulo": "¿Qué son los intereses?", "claves": ["interes"],
     "texto": "Los intereses son un costo extra por usar dinero prestado. Entre más tiempo tardas en pagar, normalmente pagas más."},
    {"id": "fecha_pago", "titulo": "Fecha de pago", "claves": ["fecha de pago", "pagar a tiempo", "puntual"],
     "texto": "La fecha de pago es el día límite para pagar. Pagar puntualmente ayuda a evitar cobros extra y a mantener una buena historia de pagos."},
    {"id": "historial", "titulo": "¿Qué es el historial crediticio?", "claves": ["historial"],
     "texto": "El historial crediticio es el registro de cómo has pagado los créditos que has tenido. Kiki Pay no crea historial por sí misma: se forma con productos financieros reales de instituciones que reportan su información. No hace falta endeudarse para tenerlo; primero aprende y decide con calma."},
    {"id": "sic", "titulo": "Sociedades de información crediticia", "claves": ["sociedad", "buro", "buro de credito", "circulo de credito"],
     "texto": "Las sociedades de información crediticia son empresas autorizadas que reúnen cómo pagas tus créditos. En México, por ejemplo, existen Buró de Crédito y Círculo de Crédito. Las instituciones las consultan cuando alguien pide un crédito."},
    {"id": "incumplir", "titulo": "Si no puedo pagar a tiempo", "claves": ["incumpl", "no pagar", "atraso", "retraso"],
     "texto": "Si no pagas a tiempo pueden cobrarte más, y tu historial puede verse afectado. Si ves que no vas a poder pagar, habla pronto con la institución y con una persona de confianza."},
]

ASESORIA_CLAVES = ["invert", "inversion", "cripto", "bitcoin", "acciones", "apuesta", "bolsa de valores"]
SENSIBLE_CLAVES = ["nip", "contrasena", "password", "cvv", "clabe", "numero de tarjeta", "codigo de seguridad", "token"]

AVISO_SENSIBLE = ("🔒 Recuerda: no escribas aquí contraseñas, NIP, números de tarjeta ni claves. "
                  "Kiki nunca necesita esos datos.")
TEXTO_ASESORIA = ("Kiki no da recomendaciones personales de inversión ni de decisiones de alto riesgo. "
                  "Puedo explicarte qué significan las palabras. Para decidir sobre tu dinero, conversa con una persona de confianza "
                  "o con una institución financiera oficial.")
TEXTO_SIN_RESPUESTA = ("Todavía no tengo una explicación para eso. Puedo ayudarte con dinero, ingresos, gastos, ahorro, "
                       "presupuesto, compras, cambio, cuentas, tarjetas, transferencias, seguridad y créditos.")


def _tiene_clave(texto_norm: str, claves) -> bool:
    return any(re.search(r"\b" + re.escape(c), texto_norm) for c in claves)


def buscar_respuesta(pregunta: str) -> dict:
    """Devuelve {'tipo','titulo','texto','aviso'}. tipo: vacia|asesoria|respuesta|nada."""
    q = normalizar(pregunta)
    if not q:
        return {"tipo": "vacia", "titulo": "", "texto": "Escribe una pregunta o una palabra sobre el tema.", "aviso": ""}
    aviso = AVISO_SENSIBLE if (_tiene_clave(q, SENSIBLE_CLAVES) or re.search(r"\d{8,}", pregunta)) else ""
    if _tiene_clave(q, ASESORIA_CLAVES):
        return {"tipo": "asesoria", "titulo": "Sobre decisiones de inversión", "texto": TEXTO_ASESORIA, "aviso": aviso}
    mejor, mejor_puntos = None, 0
    for entrada in BASE_KIKI:
        puntos = sum(len(c) for c in entrada["claves"] if re.search(r"\b" + re.escape(c), q))
        if puntos > mejor_puntos:
            mejor, mejor_puntos = entrada, puntos
    if mejor:
        return {"tipo": "respuesta", "titulo": mejor["titulo"], "texto": mejor["texto"], "aviso": aviso}
    return {"tipo": "nada", "titulo": "", "texto": TEXTO_SIN_RESPUESTA, "aviso": aviso}


def entrada_por_id(id_):
    return next((e for e in BASE_KIKI if e["id"] == id_), None)


# -------------------------------------------------------------- datos de ejemplo
def datos_demo(hoy: date):
    """Datos FICTICIOS para demostrar los módulos. Devuelve (movimientos, metas, siguiente_id)."""
    base = [
        ("Ingreso", 200, "Apoyo familiar", "Dinero de práctica", 6),
        ("Ingreso", 80, "Otros ingresos", "Ayuda en casa (ejemplo)", 4),
        ("Gasto", 35, "Educación", "Cuaderno", 5),
        ("Gasto", 18, "Alimentación", "Pan", 3),
        ("Gasto", 9, "Transporte", "Boleto de camión", 2),
        ("Gasto", 30, "Entretenimiento", "Helado", 1),
    ]
    movs, i = [], 1
    for tipo, cant, cat, desc, dias in base:
        mov, _ = crear_movimiento(tipo, cant, cat, desc, hoy - timedelta(days=dias), i)
        movs.append(mov)
        i += 1
    metas = []
    for nombre, obj, ah in (("Audífonos", 300, 120), ("Bicicleta", 2500, 400)):
        meta, _ = crear_meta(nombre, obj, ah, i)
        metas.append(meta)
        i += 1
    return movs, metas, i


# ----------------------------------------------------------- respaldo / restaurar
def exportar_estado(movimientos, metas, prefs, progreso) -> str:
    return json.dumps({
        "kiki_pay_respaldo": VERSION_RESPALDO,
        "creado": datetime.now().isoformat(timespec="seconds"),
        "movimientos": movimientos, "metas": metas,
        "preferencias": prefs, "progreso": progreso,
    }, ensure_ascii=False, indent=2)


def _prefs_validas(crudo) -> dict:
    prefs = dict(PREFS_DEFAULT)
    if not isinstance(crudo, dict):
        return prefs
    if isinstance(crudo.get("nombre"), str):
        prefs["nombre"] = crudo["nombre"][:40]
    if crudo.get("tamano") in TAMANOS:
        prefs["tamano"] = crudo["tamano"]
    for k in ("contraste", "pistas", "reducir", "pictos"):
        if isinstance(crudo.get(k), bool):
            prefs[k] = crudo[k]
    if crudo.get("modo") in MODOS:
        prefs["modo"] = crudo["modo"]
    if crudo.get("dificultad") in (1, 2, 3) and not isinstance(crudo.get("dificultad"), bool):
        prefs["dificultad"] = crudo["dificultad"]
    return prefs


def importar_estado(texto: str):
    """Valida un respaldo. Devuelve (estado, None) o (None, mensaje_de_error)."""
    if not isinstance(texto, str) or len(texto) > 2_000_000:
        return None, "El archivo es demasiado grande o no se pudo leer."
    try:
        datos = json.loads(texto)
    except (ValueError, TypeError):
        return None, "El archivo no es una copia de seguridad válida de Kiki Pay."
    if not isinstance(datos, dict) or datos.get("kiki_pay_respaldo") != VERSION_RESPALDO:
        return None, "El archivo no es una copia de seguridad válida de Kiki Pay."
    crudos_m, crudas_g = datos.get("movimientos", []), datos.get("metas", [])
    if not isinstance(crudos_m, list) or not isinstance(crudas_g, list) \
            or len(crudos_m) > MAX_REGISTROS or len(crudas_g) > MAX_REGISTROS:
        return None, "La copia tiene un formato que no se puede leer."
    contador, movs, metas = 1, [], []
    for m in crudos_m:
        if not isinstance(m, dict):
            return None, "La copia tiene movimientos con formato no válido."
        mov, err = crear_movimiento(m.get("tipo"), m.get("cantidad"), m.get("categoria"),
                                    m.get("descripcion"), m.get("fecha"), contador)
        if err:
            return None, "La copia tiene un movimiento no válido: " + err
        movs.append(mov)
        contador += 1
    for g in crudas_g:
        if not isinstance(g, dict):
            return None, "La copia tiene metas con formato no válido."
        meta, err = crear_meta(g.get("nombre"), g.get("objetivo"), g.get("ahorrado"), contador)
        if err:
            return None, "La copia tiene una meta no válida: " + err
        metas.append(meta)
        contador += 1
    progreso = dict(PROGRESO_DEFAULT)
    crudo_p = datos.get("progreso")
    if isinstance(crudo_p, dict):
        for k in progreso:
            v = crudo_p.get(k)
            if isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 10_000_000:
                progreso[k] = v
    return {"movimientos": movs, "metas": metas, "sig_id": contador,
            "prefs": _prefs_validas(datos.get("preferencias")), "progreso": progreso}, None
