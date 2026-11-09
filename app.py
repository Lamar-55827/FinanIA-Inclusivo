"""
Kiki Pay - Inclusión y Autonomía Financiera (Fase 3 corregida)
"Tu dinero, tus decisiones, tu futuro"

Interfaz en Streamlit. La lógica que se puede probar sin interfaz está en kiki_logica.py.

ALMACENAMIENTO: todo se guarda SOLO en la sesión del navegador (st.session_state).
Si se recarga la página o la app se reinicia, los datos se pierden. Para conservarlos
la persona puede descargar una copia (JSON) en "Mi experiencia" y restaurarla después.
Aún NO existe almacenamiento permanente en servidor ni panel familiar (Fase 4).
"""
import copy
import random
import re
from datetime import date

import pandas as pd
import streamlit as st

import kiki_logica as kl

st.set_page_config(page_title="Kiki Pay", page_icon="🪙", layout="wide")

SECCIONES = [
    ("inicio", "Inicio", "🏠"),
    ("dinero", "Conozco el dinero", "🪙"),
    ("compras", "Practico compras", "🛍️"),
    ("organizo", "Organizo mi dinero", "📊"),
    ("ahorro", "Mi ahorro", "🌱"),
    ("retos", "Retos", "🎮"),
    ("kiki", "Pregúntale a Kiki", "💬"),
    ("progreso", "Mi progreso", "📈"),
    ("experiencia", "Mi experiencia", "⚙️"),
]
NOMBRES_DIFICULTAD = {1: "Fácil", 2: "Media", 3: "Reto"}


# ============================================================ estado de sesión
def init_estado():
    """Crea las variables de sesión UNA vez; nunca las reinicia en cada ejecución."""
    ss = st.session_state
    ss.setdefault("movimientos", [])
    ss.setdefault("metas", [])
    ss.setdefault("sig_id", 1)
    ss.setdefault("prefs", copy.deepcopy(kl.PREFS_DEFAULT))
    ss.setdefault("progreso", copy.deepcopy(kl.PROGRESO_DEFAULT))
    ss.setdefault("seccion", "inicio")
    ss.setdefault("msgs", {})
    ss.setdefault("contador", 0)
    ss.setdefault("ej_dinero", None)
    ss.setdefault("reto", None)
    ss.setdefault("kiki_hist", [])


def nuevo_id():
    ss = st.session_state
    valor = ss.sig_id
    ss.sig_id += 1
    return valor


def nuevo_n():
    st.session_state.contador += 1
    return st.session_state.contador


def poner_msg(clave, tipo, texto):
    st.session_state.msgs[clave] = (tipo, texto)


def quitar_msg(clave):
    st.session_state.msgs.pop(clave, None)


def mostrar_msg(clave):
    m = st.session_state.msgs.get(clave)
    if m:
        {"ok": st.success, "info": st.info, "aviso": st.warning, "error": st.error}[m[0]](m[1])


def iniciar_widget(pref):
    """Los widgets de otras páginas pierden su valor; se reponen desde prefs."""
    clave = "w_" + pref
    if clave not in st.session_state:
        st.session_state[clave] = st.session_state.prefs[pref]


def cb_pref(pref):
    st.session_state.prefs[pref] = st.session_state["w_" + pref]


def ico(emoji):
    return f"{emoji} " if st.session_state.prefs["pictos"] else ""


def esc(texto):
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>$~])", r"\\\1", texto)


def hay_datos():
    ss = st.session_state
    return bool(ss.movimientos or ss.metas)


def pista(texto):
    if st.session_state.prefs["pistas"]:
        st.info("👣 " + texto)


# ================================================================ estilos (CSS)
CSS = """
<style>
.stApp { background: __BG__; }
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp li,.stApp label,
.stApp [data-testid="stMetricLabel"],.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stCaptionContainer"],.stApp summary,.stApp summary p { color: __FG__; }
.stApp p,.stApp li,.stApp label { font-size: __PX__px; }
[data-testid="stSidebar"] { background: __SIDE__; }
[data-testid="stAlert"] * { color: #111111 !important; }
div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
  min-height: 2.9rem; border-radius: 10px; font-weight: 600; border: 2px solid __BORDER__; }
.kp-hero { padding: 1.2rem 1.4rem; border-radius: 14px; border: 2px solid __BORDER__;
  background: __HERO__; margin-bottom: 1rem; }
.kp-hero h1 { margin: 0; font-size: 2rem; }
.kp-hero p { margin: .3rem 0 0 0; }
.kp-piezas { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; margin:.6rem 0 1rem 0; }
.kp-moneda { display:inline-flex; align-items:center; justify-content:center; width:4.2rem; height:4.2rem;
  border-radius:50%; border:3px solid #000; font-weight:700; color:#000 !important; background:#D9D9D9; }
.kp-moneda.kp-v1 { width:3.2rem; height:3.2rem; }
.kp-moneda.kp-v2 { width:3.6rem; height:3.6rem; }
.kp-moneda.kp-v5 { width:4rem; height:4rem; }
.kp-moneda.kp-v10 { width:4.4rem; height:4.4rem; background: radial-gradient(circle,#E8C65A 46%,#C8C8C8 47%); }
.kp-billete { display:inline-flex; align-items:center; justify-content:center; width:7rem; height:3.6rem;
  border-radius:8px; border:3px solid #000; font-weight:700; color:#000 !important; }
.kp-billete.kp-v20 { background:#9CC9F5; } .kp-billete.kp-v50 { background:#F4A6CF; }
.kp-billete.kp-v100 { background:#F29A9A; } .kp-billete.kp-v200 { background:#A7DDA0; }
__EXTRA__
</style>
"""


def construir_css(p):
    px = kl.TAMANOS.get(p["tamano"], 18)
    if p["contraste"]:
        bg, fg, side, border, hero = "#000000", "#FFFFFF", "#111111", "#FFFFFF", "#000000"
    elif p["reducir"]:
        bg, fg, side, border, hero = "#F5F5F5", "#222222", "#EBEBEB", "#9A9A9A", "#FFFFFF"
    else:
        bg, fg, side, border, hero = "#FBF9FF", "#25213A", "#F1ECFA", "#B9AEDD", \
            "linear-gradient(135deg,#EDE7FB,#E3F4F1)"
    extra = ""
    if p["reducir"]:
        extra = "*,*::before,*::after{animation:none !important;transition:none !important;scroll-behavior:auto !important;}"
    return (CSS.replace("__BG__", bg).replace("__FG__", fg).replace("__SIDE__", side)
            .replace("__BORDER__", border).replace("__HERO__", hero)
            .replace("__PX__", str(px)).replace("__EXTRA__", extra))


def html_piezas(items):
    partes = []
    for tipo, valor, n in items:
        clase = "kp-billete" if tipo == "billete" else "kp-moneda"
        for _ in range(n):
            partes.append(f'<span class="{clase} kp-v{valor}" role="img" '
                          f'aria-label="{tipo} de {valor} pesos">${valor}</span>')
    return '<div class="kp-piezas">' + "".join(partes) + "</div>"


def mostrar_piezas(items, titulo=None):
    """Muestra piezas de dinero según el modo elegido en 'Mi forma de aprender'."""
    modo = st.session_state.prefs["modo"]
    if titulo:
        st.markdown(f"**{titulo}**")
    if modo == "Solo números":
        st.write(kl.describir_piezas(items))
        return
    st.markdown(html_piezas(items), unsafe_allow_html=True)
    if modo == "Pictogramas":
        st.write("Cuenta paso a paso: " + kl.conteo_progresivo(items))
    else:
        st.write("Operación: " + kl.expresion_suma(items))


# ================================================================ barra lateral
def etiqueta_seccion(id_):
    _, nombre, emoji = next(s for s in SECCIONES if s[0] == id_)
    return f"{emoji} {nombre}" if st.session_state.prefs["pictos"] else nombre


def barra_lateral():
    p = st.session_state.prefs
    st.sidebar.title(ico("🪙") + "Kiki Pay")
    st.sidebar.caption("Tu dinero, tus decisiones, tu futuro")
    if p["nombre"].strip():
        st.sidebar.markdown(f"¡Hola, {esc(p['nombre'].strip())}!")
    st.sidebar.radio("Elige una sección:", [s[0] for s in SECCIONES],
                     format_func=etiqueta_seccion, key="seccion")
    with st.sidebar.expander("Mi forma de aprender", expanded=False):
        iniciar_widget("modo")
        st.radio("¿Cómo quiero ver el dinero?", kl.MODOS, key="w_modo",
                 on_change=cb_pref, args=("modo",))
        iniciar_widget("dificultad")
        st.select_slider("Dificultad de los ejercicios", options=[1, 2, 3],
                         format_func=lambda n: NOMBRES_DIFICULTAD[n], key="w_dificultad",
                         on_change=cb_pref, args=("dificultad",))
    st.sidebar.caption("Datos de práctica. No escribas datos bancarios reales.")


# ============================================================== callbacks datos
def cb_ir(destino):
    st.session_state["seccion"] = destino


def cb_cargar_demo():
    ss = st.session_state
    ss.movimientos, ss.metas, ss.sig_id = kl.datos_demo(date.today())
    ss["conf_demo"] = False
    poner_msg("datos", "ok", "Listo: cargué datos FICTICIOS de ejemplo para practicar.")


def cb_borrar_todo():
    ss = st.session_state
    ss.movimientos, ss.metas, ss.sig_id = [], [], 1
    ss.progreso = copy.deepcopy(kl.PROGRESO_DEFAULT)
    ss.kiki_hist, ss.ej_dinero, ss.reto = [], None, None
    ss["conf_borrar"] = False
    poner_msg("datos", "ok", "Borré tus datos de práctica. Tus preferencias se conservan.")


def cb_restaurar():
    ss = st.session_state
    archivo = ss.get("w_respaldo")
    if archivo is None:
        poner_msg("datos", "aviso", "Primero elige un archivo de copia de seguridad.")
        return
    try:
        texto = archivo.getvalue().decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        poner_msg("datos", "error", "No pude leer ese archivo.")
        return
    estado, error = kl.importar_estado(texto)
    if error:
        poner_msg("datos", "error", error)
        return
    ss.movimientos, ss.metas, ss.sig_id = estado["movimientos"], estado["metas"], estado["sig_id"]
    ss.prefs, ss.progreso = estado["prefs"], estado["progreso"]
    for pref, valor in ss.prefs.items():
        ss["w_" + pref] = valor
    ss.ej_dinero, ss.reto = None, None
    ss["conf_restaurar"] = False
    poner_msg("datos", "ok", "Copia restaurada correctamente.")


# ===================================================================== páginas
def pagina_inicio():
    ss = st.session_state
    st.markdown(
        '<div class="kp-hero"><h1>Kiki Pay</h1><p><b>Tu dinero, tus decisiones, tu futuro</b></p>'
        '<p>Practica a tu ritmo: reconoce el dinero, haz compras de práctica, organiza lo que recibes y gastas, '
        'y ahorra para tus metas.</p></div>', unsafe_allow_html=True)
    nombre = ss.prefs["nombre"].strip()
    st.subheader(f"¡Hola, {esc(nombre)}!" if nombre else "¡Hola!")
    ingresos, gastos, saldo = kl.totales(ss.movimientos)
    ahorro = sum(m["ahorrado"] for m in ss.metas)
    c1, c2, c3 = st.columns(3)
    c1.metric("Dinero disponible (práctica)", kl.formato_dinero(saldo))
    c2.metric("Ahorrado en mis metas", kl.formato_dinero(ahorro))
    c3.metric("Metas", len(ss.metas))
    mostrar_msg("datos")
    if not hay_datos():
        pista("Aún no hay datos. Puedes empezar en blanco o cargar un ejemplo ficticio para ver cómo funciona.")
        st.button("Cargar ejemplo ficticio", on_click=cb_cargar_demo, key="inicio_demo")
    st.subheader("¿Por dónde quieres empezar?")
    tarjetas = [
        ("dinero", "🪙", "Conozco el dinero", "Monedas y billetes, sumar y restar."),
        ("compras", "🛍️", "Practico compras", "Elige un producto y calcula tu cambio."),
        ("organizo", "📊", "Organizo mi dinero", "Anota lo que recibes y lo que gastas."),
        ("ahorro", "🌱", "Mi ahorro", "Crea metas y mira tu avance."),
        ("retos", "🎮", "Retos", "Practica con situaciones cotidianas."),
        ("kiki", "💬", "Pregúntale a Kiki", "Explicaciones sencillas."),
    ]
    for fila in range(0, len(tarjetas), 3):
        cols = st.columns(3)
        for col, (id_, emoji, titulo, desc) in zip(cols, tarjetas[fila:fila + 3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{ico(emoji)}{titulo}**")
                    st.write(desc)
                    st.button("Abrir", key=f"ir_{id_}", on_click=cb_ir, args=(id_,))


# ---- Conozco el dinero
def cb_nuevo_dinero():
    ss = st.session_state
    ej = kl.generar_ejercicio_dinero(ss.prefs["dificultad"], random.Random())
    ej["n"] = nuevo_n()
    ej["resuelto"] = False
    ss.ej_dinero = ej
    quitar_msg("dinero")


def cb_comprobar_dinero():
    ss = st.session_state
    ej = ss.ej_dinero
    if not ej:
        return
    eleccion = ss.get(f"resp_dinero_{ej['n']}")
    if eleccion is None:
        poner_msg("dinero", "aviso", "Elige una respuesta y vuelve a pulsar «Comprobar».")
        return
    ss.progreso["dinero_total"] += 1
    if int(eleccion) == ej["total"]:
        ss.progreso["dinero_ok"] += 1
        ej["resuelto"] = True
        poner_msg("dinero", "ok",
                  f"¡Muy bien! Son {kl.formato_dinero(ej['total'])}. "
                  f"{kl.expresion_suma(ej['items'])} = {ej['total']}.")
    else:
        poner_msg("dinero", "info",
                  "Casi. Cuenta otra vez, una pieza a la vez. Puedes intentarlo de nuevo cuando quieras.")


def cb_comprobar_suma():
    ss = st.session_state
    a, b, op = ss.get("sum_a"), ss.get("sum_b"), ss.get("sum_op", "Sumar")
    r = ss.get("sum_res")
    if a is None or b is None or r is None:
        return
    if op == "Restar" and b > a:
        poner_msg("suma", "aviso", "Para restar, elige una primera cantidad mayor o igual que la segunda.")
        return
    esperado = a + b if op == "Sumar" else a - b
    ss.progreso["suma_total"] += 1
    if int(r) == esperado:
        ss.progreso["suma_ok"] += 1
        simbolo = "+" if op == "Sumar" else "−"
        poner_msg("suma", "ok", f"¡Correcto! {a} {simbolo} {b} = {esperado}.")
    else:
        poner_msg("suma", "info", "No es esa todavía. Inténtalo otra vez; puedes usar tus dedos o dibujar las monedas.")


def limpiar_suma():
    quitar_msg("suma")


def pagina_dinero():
    ss = st.session_state
    st.header(ico("🪙") + "Conozco el dinero")
    st.caption("Cambia entre pictogramas, imagen con número o solo números en «Mi forma de aprender» (barra lateral).")
    pista("Mira las monedas y billetes, cuenta cuánto dinero hay en total y elige la respuesta.")
    if ss.ej_dinero is None or ss.ej_dinero["nivel"] != ss.prefs["dificultad"]:
        cb_nuevo_dinero()
    ej = ss.ej_dinero
    mostrar_piezas(ej["items"], "¿Cuánto dinero hay aquí?")
    st.radio("Elige tu respuesta:", ej["opciones"], index=None, format_func=kl.formato_dinero,
             key=f"resp_dinero_{ej['n']}", horizontal=True, disabled=ej["resuelto"])
    c1, c2 = st.columns(2)
    c1.button("Comprobar", key="btn_comprobar_dinero", on_click=cb_comprobar_dinero,
              disabled=ej["resuelto"], type="primary")
    c2.button("Otro ejercicio", key="btn_nuevo_dinero", on_click=cb_nuevo_dinero)
    mostrar_msg("dinero")
    if ej["resuelto"]:
        st.write("Hay: " + kl.describir_piezas(ej["items"]) + ".")

    st.divider()
    st.subheader(ico("➕") + "Practico sumas y restas")
    st.radio("Operación", ["Sumar", "Restar"], key="sum_op", horizontal=True, on_change=limpiar_suma)
    valores = [1, 2, 5, 10, 20, 50]
    ss.setdefault("sum_a", 10)
    ss.setdefault("sum_b", 5)
    ca, cb = st.columns(2)
    ca.selectbox("Primera cantidad", valores, key="sum_a", on_change=limpiar_suma)
    cb.selectbox("Segunda cantidad", valores, key="sum_b", on_change=limpiar_suma)
    simbolo = "+" if ss.get("sum_op", "Sumar") == "Sumar" else "−"
    st.write(f"**{ss.sum_a} {simbolo} {ss.sum_b} = ?**")
    st.number_input("Tu resultado", min_value=0, max_value=200, step=1, key="sum_res", on_change=limpiar_suma)
    st.button("Comprobar operación", key="btn_suma", on_click=cb_comprobar_suma, type="primary")
    mostrar_msg("suma")


# ---- Practico compras
def cb_registrar_compra():
    ss = st.session_state
    nombre = ss.get("compra_prod")
    if nombre not in kl.PRODUCTOS:
        return
    _emoji, precio, categoria = kl.PRODUCTOS[nombre]
    mov, error = kl.crear_movimiento("Gasto", precio, categoria, f"Compra de práctica: {nombre}",
                                     date.today(), ss.sig_id)
    if error:
        poner_msg("compras", "error", error)
        return
    ss.sig_id += 1
    ss.movimientos.append(mov)
    ss.progreso["compras"] += 1
    poner_msg("compras", "ok", f"Registré «{nombre}» como gasto de práctica por {kl.formato_dinero(precio)}. "
              "Puedes verlo en «Organizo mi dinero».")


def pagina_compras():
    ss = st.session_state
    st.header(ico("🛍️") + "Practico compras")
    pista("1) Elige un producto. 2) Elige con cuánto dinero pagas. 3) Mira si alcanza y cuánto te regresan.")
    nombres = list(kl.PRODUCTOS)
    ss.setdefault("compra_pago", 50)
    st.selectbox("Producto", nombres, key="compra_prod",
                 format_func=lambda n: f"{kl.PRODUCTOS[n][0]} {n} — {kl.formato_dinero(kl.PRODUCTOS[n][1])}")
    st.select_slider("Dinero que entrego", options=[10, 20, 50, 100, 200, 500], key="compra_pago",
                     format_func=kl.formato_dinero)
    nombre, pago = ss.compra_prod, ss.compra_pago
    emoji, precio, _ = kl.PRODUCTOS[nombre]
    r = kl.calcular_cambio(precio, pago)
    c1, c2, c3 = st.columns(3)
    c1.metric("Precio", kl.formato_dinero(precio))
    c2.metric("Entrego", kl.formato_dinero(pago))
    if r["suficiente"]:
        c3.metric("Mi cambio", kl.formato_dinero(r["cambio"]))
        st.success(f"Sí alcanza. {pago} − {precio} = {r['cambio']}.")
        if r["cambio"] > 0:
            mostrar_piezas(kl.desglose_cambio(r["cambio"]), "Te regresan:")
    else:
        c3.metric("Me falta", kl.formato_dinero(r["falta"]))
        st.warning(f"No alcanza todavía: faltan {kl.formato_dinero(r['falta'])}. Puedes entregar más dinero o elegir otro producto.")
    _i, _g, saldo = kl.totales(ss.movimientos)
    if hay_datos():
        if saldo >= precio:
            st.write(f"Con tu dinero disponible de práctica ({kl.formato_dinero(saldo)}) sí podrías comprarlo.")
        else:
            st.write(f"Tu dinero disponible de práctica es {kl.formato_dinero(saldo)}: por ahora no alcanzaría.")
    st.button("Registrar esta compra como gasto de práctica", key="btn_registrar_compra",
              on_click=cb_registrar_compra, disabled=not r["suficiente"])
    mostrar_msg("compras")
    st.divider()
    st.subheader(ico("⚖️") + "Comparo productos")
    elegidos = st.multiselect("Elige dos o más productos", nombres, key="compare_prods")
    if len(elegidos) >= 2:
        filas = sorted(({"Producto": f"{kl.PRODUCTOS[n][0]} {n}", "Precio": kl.PRODUCTOS[n][1]} for n in elegidos),
                       key=lambda f: f["Precio"])
        st.dataframe(pd.DataFrame(filas), hide_index=True)
        st.write(f"El que cuesta menos es **{filas[0]['Producto']}** ({kl.formato_dinero(filas[0]['Precio'])}).")
    else:
        st.caption("Elige al menos dos productos para compararlos.")


# ---- Organizo mi dinero
def cb_borrar_movimiento():
    ss = st.session_state
    id_ = ss.get("borrar_mov")
    if id_ is None:
        poner_msg("movs", "aviso", "Elige primero el movimiento que quieres borrar.")
        return
    ss.movimientos = [m for m in ss.movimientos if m["id"] != id_]
    ss["borrar_mov"] = None
    poner_msg("movs", "ok", "Movimiento borrado.")


def cb_borrar_movimientos_todos():
    ss = st.session_state
    ss.movimientos = []
    ss["conf_borrar_movs"] = False
    poner_msg("movs", "ok", "Borré todos los movimientos.")


def pagina_organizo():
    ss = st.session_state
    st.header(ico("📊") + "Organizo mi dinero")
    pista("Primero elige si es un ingreso (dinero que recibes) o un gasto (dinero que pagas). Luego llena el formulario y pulsa «Guardar».")
    ss.setdefault("mov_tipo", "Ingreso")
    st.radio("¿Qué quieres anotar?", ["Ingreso", "Gasto"], key="mov_tipo", horizontal=True)
    tipo = ss.mov_tipo
    with st.form("form_mov", clear_on_submit=True):
        categoria = st.selectbox("Categoría", kl.CATEGORIAS[tipo], key="mov_cat")
        cantidad = st.number_input("Cantidad ($)", min_value=0.0, step=1.0, format="%.2f", key="mov_cant")
        descripcion = st.text_input("Descripción (opcional)", max_chars=kl.MAX_DESCRIPCION, key="mov_desc")
        fecha = st.date_input("Fecha", value=date.today(), key="mov_fecha")
        enviado = st.form_submit_button("Guardar", type="primary")
    if enviado:
        mov, error = kl.crear_movimiento(tipo, cantidad, categoria, descripcion, fecha, ss.sig_id)
        if error:
            st.error(error)
        else:
            ss.sig_id += 1
            ss.movimientos.append(mov)
            st.success(f"Guardado: {tipo.lower()} de {kl.formato_dinero(mov['cantidad'])} en «{mov['categoria']}».")
    ingresos, gastos, saldo = kl.totales(ss.movimientos)
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos totales", kl.formato_dinero(ingresos))
    c2.metric("Gastos totales", kl.formato_dinero(gastos))
    c3.metric("Saldo disponible", kl.formato_dinero(saldo))
    if saldo < 0:
        st.warning("Gastaste más de lo que registraste como ingreso. Revisa tus movimientos o planea con calma tus próximos gastos.")
    mostrar_msg("movs")
    if not ss.movimientos:
        st.info("Todavía no hay movimientos. Guarda el primero con el formulario o carga el ejemplo en «Mi experiencia».")
        return
    por_cat = kl.gastos_por_categoria(ss.movimientos)
    if por_cat:
        st.subheader("¿En qué gasto mi dinero?")
        st.bar_chart(pd.Series(por_cat, name="Gasto"))
        for cat, val in por_cat.items():
            st.write(f"• {cat}: {kl.formato_dinero(val)} ({val / gastos * 100:.0f}% de tus gastos)")
    st.subheader("Mis movimientos")
    df = pd.DataFrame([{"Fecha": m["fecha"], "Tipo": m["tipo"], "Categoría": m["categoria"],
                        "Descripción": m["descripcion"], "Cantidad": m["cantidad"], "_id": m["id"]}
                       for m in ss.movimientos]).sort_values(["Fecha", "_id"], ascending=False)
    st.dataframe(df.drop(columns="_id"), hide_index=True)
    st.download_button("Descargar mis movimientos (CSV)", df.drop(columns="_id").to_csv(index=False).encode("utf-8-sig"),
                       file_name="kiki_pay_movimientos.csv", mime="text/csv", key="dl_csv")
    with st.expander("Borrar movimientos"):
        ids = [m["id"] for m in ss.movimientos]
        etiquetas = {m["id"]: f"{m['fecha']} · {m['tipo']} · {kl.formato_dinero(m['cantidad'])} · {m['descripcion']}"
                     for m in ss.movimientos}
        st.selectbox("Movimiento a borrar", ids, index=None, key="borrar_mov",
                     format_func=lambda i: etiquetas[i], placeholder="Elige uno")
        st.button("Borrar el movimiento elegido", key="btn_borrar_mov", on_click=cb_borrar_movimiento)
        st.checkbox("Quiero borrar TODOS los movimientos", key="conf_borrar_movs")
        st.button("Borrar todos", key="btn_borrar_movs_todos", on_click=cb_borrar_movimientos_todos,
                  disabled=not ss.get("conf_borrar_movs", False))


# ---- Mi ahorro
def cb_agregar_ahorro(id_):
    ss = st.session_state
    meta = next((m for m in ss.metas if m["id"] == id_), None)
    if meta is None:
        return
    nueva, error = kl.agregar_ahorro(meta, ss.get(f"meta_add_{id_}", 0))
    if error:
        poner_msg(f"meta_{id_}", "aviso", error)
        return
    ss.metas = [nueva if m["id"] == id_ else m for m in ss.metas]
    ss[f"meta_add_{id_}"] = 0.0
    poner_msg(f"meta_{id_}", "ok", kl.mensaje_meta(nueva))


def cb_borrar_meta(id_):
    ss = st.session_state
    ss.metas = [m for m in ss.metas if m["id"] != id_]
    quitar_msg(f"meta_{id_}")


def pagina_ahorro():
    ss = st.session_state
    st.header(ico("🌱") + "Mi ahorro")
    pista("Crea una meta, escribe cuánto cuesta y agrega lo que vayas ahorrando. La barra te muestra tu avance.")
    with st.form("form_meta", clear_on_submit=True):
        nombre = st.text_input("¿Qué quieres lograr?", max_chars=60, key="meta_nombre",
                               placeholder="Por ejemplo: audífonos")
        objetivo = st.number_input("¿Cuánto cuesta? ($)", min_value=0.0, step=10.0, format="%.2f", key="meta_obj")
        inicial = st.number_input("¿Cuánto llevas ahorrado? ($)", min_value=0.0, step=5.0, format="%.2f", key="meta_ini")
        enviado = st.form_submit_button("Crear meta", type="primary")
    if enviado:
        meta, error = kl.crear_meta(nombre, objetivo, inicial, ss.sig_id)
        if error:
            st.error(error)
        else:
            ss.sig_id += 1
            ss.metas.append(meta)
            st.success(f"Meta «{meta['nombre']}» creada.")
    if not ss.metas:
        st.info("Todavía no tienes metas. Crea la primera arriba.")
        return
    for meta in list(ss.metas):
        id_ = meta["id"]
        with st.container(border=True):
            st.subheader(esc(meta["nombre"]))
            st.progress(kl.progreso_meta(meta))
            st.write(f"Llevas **{kl.formato_dinero(meta['ahorrado'])}** de **{kl.formato_dinero(meta['objetivo'])}** "
                     f"({kl.progreso_meta(meta) * 100:.0f}%). Te faltan **{kl.formato_dinero(kl.falta_meta(meta))}**.")
            st.caption(kl.mensaje_meta(meta))
            ss.setdefault(f"meta_add_{id_}", 0.0)
            ss.setdefault(f"meta_sem_{id_}", 10.0)
            c1, c2 = st.columns([2, 1])
            c1.number_input("Cantidad que agrego ($)", min_value=0.0, step=5.0, format="%.2f", key=f"meta_add_{id_}")
            c2.button("Agregar al ahorro", key=f"btn_add_{id_}", on_click=cb_agregar_ahorro, args=(id_,), type="primary")
            mostrar_msg(f"meta_{id_}")
            if kl.falta_meta(meta) > 0:
                st.number_input("¿Cuánto podría ahorrar por semana? ($)", min_value=0.0, step=5.0, format="%.2f",
                                key=f"meta_sem_{id_}")
                semanas = kl.semanas_para_meta(kl.falta_meta(meta), ss[f"meta_sem_{id_}"])
                if semanas:
                    st.write(f"Ahorrando esa cantidad cada semana, lo lograrías en **{semanas} semana(s)**.")
            st.button("Borrar esta meta", key=f"btn_del_{id_}", on_click=cb_borrar_meta, args=(id_,))


# ---- Retos
def cb_nuevo_reto():
    ss = st.session_state
    reto = kl.generar_reto(ss.prefs["dificultad"], random.Random())
    reto["n"] = nuevo_n()
    reto["resuelto"] = False
    ss.reto = reto
    quitar_msg("reto")


def cb_comprobar_reto():
    ss = st.session_state
    reto = ss.reto
    if not reto:
        return
    eleccion = ss.get(f"resp_reto_{reto['n']}")
    if eleccion is None:
        poner_msg("reto", "aviso", "Elige una respuesta y vuelve a pulsar «Comprobar».")
        return
    ss.progreso["retos_total"] += 1
    if eleccion == reto["correcta"]:
        ss.progreso["retos_ok"] += 1
        reto["resuelto"] = True
        poner_msg("reto", "ok", "¡Muy bien! " + reto["explicacion"])
    else:
        poner_msg("reto", "info", "Todavía no. " + reto["pista"] + " Puedes intentarlo otra vez.")


def pagina_retos():
    ss = st.session_state
    st.header(ico("🎮") + "Retos")
    pista("Lee con calma, elige una respuesta y pulsa «Comprobar». Si te equivocas, puedes intentarlo otra vez.")
    if ss.reto is None or ss.reto["nivel"] != ss.prefs["dificultad"]:
        cb_nuevo_reto()
    reto = ss.reto
    st.subheader(reto["pregunta"])
    st.radio("Elige tu respuesta:", reto["opciones"], index=None, key=f"resp_reto_{reto['n']}",
             disabled=reto["resuelto"])
    c1, c2 = st.columns(2)
    c1.button("Comprobar", key="btn_comprobar_reto", on_click=cb_comprobar_reto,
              disabled=reto["resuelto"], type="primary")
    c2.button("Nuevo reto", key="btn_nuevo_reto", on_click=cb_nuevo_reto)
    mostrar_msg("reto")
    pr = ss.progreso
    st.caption(f"Has acertado {pr['retos_ok']} de {pr['retos_total']} intentos. Cada intento te ayuda a aprender.")


# ---- Kiki
def cb_explicar_tema():
    ss = st.session_state
    entrada = kl.entrada_por_id(ss.get("kiki_tema"))
    if entrada is None:
        return
    ss.kiki_hist.insert(0, {"pregunta": entrada["titulo"], "titulo": entrada["titulo"],
                            "texto": entrada["texto"], "aviso": "", "tipo": "respuesta"})
    del ss.kiki_hist[8:]


def pagina_kiki():
    ss = st.session_state
    st.header(ico("💬") + "Pregúntale a Kiki")
    st.caption("Kiki responde con explicaciones preparadas (sin internet ni servicios de pago). "
               "No da asesoría personalizada y nunca necesita tus datos bancarios.")
    with st.form("form_kiki", clear_on_submit=True):
        pregunta = st.text_input("Escribe tu pregunta", max_chars=200, key="kiki_q",
                                 placeholder="Por ejemplo: ¿qué es ahorrar?")
        enviado = st.form_submit_button("Preguntar a Kiki", type="primary")
    if enviado:
        resp = kl.buscar_respuesta(pregunta)
        resp["pregunta"] = pregunta.strip()
        ss.kiki_hist.insert(0, resp)
        del ss.kiki_hist[8:]
    ids = [e["id"] for e in kl.BASE_KIKI]
    st.selectbox("O elige un tema", ids, index=None, key="kiki_tema", placeholder="Elige un tema",
                 format_func=lambda i: kl.entrada_por_id(i)["titulo"])
    st.button("Explicar este tema", key="btn_kiki_tema", on_click=cb_explicar_tema)
    if not ss.kiki_hist:
        st.info("Aquí aparecerán las respuestas de Kiki.")
    for r in ss.kiki_hist:
        with st.container(border=True):
            if r.get("pregunta"):
                st.caption("Tu pregunta: " + r["pregunta"])
            if r.get("titulo"):
                st.markdown(f"**{r['titulo']}**")
            st.write(r["texto"])
            if r.get("aviso"):
                st.warning(r["aviso"])


# ---- Mi progreso
def pagina_progreso():
    ss = st.session_state
    st.header(ico("📈") + "Mi progreso")
    st.caption("Esto lo ves solo tú, en esta sesión. Todavía no existe un panel para familiares (llegará en una fase posterior).")
    ingresos, gastos, saldo = kl.totales(ss.movimientos)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", kl.formato_dinero(ingresos))
    c2.metric("Gastos", kl.formato_dinero(gastos))
    c3.metric("Disponible", kl.formato_dinero(saldo))
    c4.metric("Ahorrado en metas", kl.formato_dinero(sum(m["ahorrado"] for m in ss.metas)))
    st.subheader("Lo que he practicado")
    st.dataframe(pd.DataFrame(kl.habilidades(ss.progreso)), hide_index=True)
    if ss.metas:
        st.subheader("Mis metas")
        for m in ss.metas:
            st.write(f"• {esc(m['nombre'])}: {kl.progreso_meta(m) * 100:.0f}% ({kl.formato_dinero(m['ahorrado'])} de {kl.formato_dinero(m['objetivo'])})")


# ---- Mi experiencia
def pagina_experiencia():
    ss = st.session_state
    st.header(ico("⚙️") + "Mi experiencia")
    st.caption("Los cambios se aplican enseguida.")
    iniciar_widget("nombre")
    st.text_input("Mi nombre o apodo (opcional)", max_chars=40, key="w_nombre", on_change=cb_pref, args=("nombre",))
    iniciar_widget("tamano")
    st.select_slider("Tamaño de letra", options=list(kl.TAMANOS), key="w_tamano", on_change=cb_pref, args=("tamano",))
    for pref, texto in (("contraste", "Alto contraste"),
                        ("pistas", "Mostrar instrucciones paso a paso"),
                        ("reducir", "Reducir estímulos visuales (sin degradados ni movimiento)"),
                        ("pictos", "Mostrar pictogramas (íconos)")):
        iniciar_widget(pref)
        st.toggle(texto, key="w_" + pref, on_change=cb_pref, args=(pref,))
    st.caption("El modo de ver el dinero y la dificultad se cambian en «Mi forma de aprender», en la barra lateral.")

    st.divider()
    st.subheader("Mis datos")
    st.info("Tus datos viven solo en esta sesión del navegador. Si recargas la página se pierden. "
            "Descarga una copia para guardarlos y restáuralos cuando quieras. La copia no incluye datos bancarios.")
    mostrar_msg("datos")
    copia = kl.exportar_estado(ss.movimientos, ss.metas, ss.prefs, ss.progreso)
    st.download_button("Descargar mi copia de seguridad", copia, file_name="kiki_pay_respaldo.json",
                       mime="application/json", key="dl_respaldo")
    st.file_uploader("Restaurar una copia de seguridad (.json)", type=["json"], key="w_respaldo")
    existe = hay_datos()
    if existe:
        st.checkbox("Entiendo que se reemplazarán mis datos actuales", key="conf_restaurar")
    st.button("Restaurar copia", key="btn_restaurar", on_click=cb_restaurar,
              disabled=existe and not ss.get("conf_restaurar", False))
    st.subheader("Ejemplo ficticio")
    if existe:
        st.checkbox("Entiendo que se reemplazarán mis datos actuales", key="conf_demo")
    st.button("Cargar datos de ejemplo", key="btn_demo", on_click=cb_cargar_demo,
              disabled=existe and not ss.get("conf_demo", False))
    st.subheader("Empezar de cero")
    st.checkbox("Quiero borrar todos mis datos de práctica", key="conf_borrar")
    st.button("Borrar mis datos", key="btn_borrar_todo", on_click=cb_borrar_todo,
              disabled=not ss.get("conf_borrar", False))


PAGINAS = {
    "inicio": pagina_inicio, "dinero": pagina_dinero, "compras": pagina_compras,
    "organizo": pagina_organizo, "ahorro": pagina_ahorro, "retos": pagina_retos,
    "kiki": pagina_kiki, "progreso": pagina_progreso, "experiencia": pagina_experiencia,
}


def main():
    init_estado()
    st.markdown(construir_css(st.session_state.prefs), unsafe_allow_html=True)
    barra_lateral()
    PAGINAS.get(st.session_state.seccion, pagina_inicio)()
    st.divider()
    st.caption("Kiki Pay es una herramienta educativa con datos de práctica. No realiza operaciones financieras reales.")


main()
