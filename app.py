import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="FinanIA Inclusivo", page_icon="🌈", layout="wide")

# Estado de la sesión: los datos son temporales y pueden reiniciarse.
DEFAULTS = {
    "movimientos": [],
    "meta_ahorro": 500.0,
    "ahorro_actual": 0.0,
    "nombre": "",
    "tamano_letra": "Mediana",
    "alto_contraste": False,
    "mostrar_pistas": True,
    "modo_demo": True,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Apariencia accesible
font_sizes = {"Pequeña": 16, "Mediana": 18, "Grande": 21, "Muy grande": 24}
font_px = font_sizes[st.session_state.tamano_letra]
if st.session_state.alto_contraste:
    bg, fg, card, border = "#101820", "#FFFFFF", "#202D38", "#FFFFFF"
else:
    bg, fg, card, border = "#FBF8FF", "#263238", "#FFFFFF", "#DDD6EA"

st.markdown(f"""
<style>
.stApp {{ background: {bg}; color: {fg}; }}
html, body, [class*="st-"], p, label, li {{ font-size: {font_px}px; }}
.block-container {{ max-width: 1180px; padding-top: 1.4rem; padding-bottom: 3rem; }}
.finania-hero {{ background: linear-gradient(120deg,#DCCBFF,#BDEFE7);
color:#24313A; padding:1.35rem 1.5rem; border-radius:20px; margin-bottom:1rem; }}
.finania-card {{ background:{card}; color:{fg}; border:1px solid {border};
border-radius:16px; padding:1rem; min-height:120px; }}
div.stButton > button, div.stFormSubmitButton > button {{
min-height:2.8rem; border-radius:12px; font-weight:600; }}
</style>
""", unsafe_allow_html=True)

def money(value):
    return f"${value:,.2f} MXN"

def hint(message):
    if st.session_state.mostrar_pistas:
        st.info("**Paso a paso:** " + message)

def totals():
    income = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"] == "Ingreso")
    expense = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"] == "Gasto")
    return income, expense, income - expense

def add_movement(kind, concept, category, amount):
    st.session_state.movimientos.append({
        "Fecha": str(date.today()),
        "Tipo": kind,
        "Concepto": concept or category,
        "Categoría": category,
        "Cantidad": float(amount),
    })

st.markdown("""
<div class="finania-hero">
<h1>🌈 FinanIA Inclusivo</h1>
<h3>Aprender sobre el dinero, paso a paso y a tu propio ritmo.</h3>
<p>Explora, practica y vuelve a intentar cuando lo necesites. No hay prisa.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("🌈 FinanIA Inclusivo")
st.sidebar.caption("Tu espacio para aprender sobre el dinero")
if st.session_state.nombre.strip():
    st.sidebar.write(f"¡Hola, {st.session_state.nombre.strip()}!")

section = st.sidebar.radio("Elige una sección:", [
    "🏠 Inicio", "🪙 Conozco el dinero", "🛍️ Practico compras",
    "📊 Organizo mi dinero", "🌱 Mi ahorro", "🎮 Retos y juegos",
    "💬 Ayuda FinanIA", "⚙️ Mi experiencia"
])

# Modo demostración: carga datos ficticios para una presentación.
st.sidebar.divider()
demo_choice = st.sidebar.toggle("Cargar ejemplo de demostración", value=False)
if demo_choice and not st.session_state.modo_demo:
    st.session_state.movimientos = [
        {"Fecha": str(date.today()), "Tipo": "Ingreso", "Concepto": "Dinero de práctica",
         "Categoría": "Otro", "Cantidad": 200.0},
        {"Fecha": str(date.today()), "Tipo": "Gasto", "Concepto": "Cuaderno",
         "Categoría": "Educación", "Cantidad": 35.0},
    ]
    st.session_state.ahorro_actual = 120.0
    st.session_state.meta_ahorro = 300.0
    st.session_state.modo_demo = True
elif not demo_choice and st.session_state.modo_demo:
    st.session_state.movimientos = []
    st.session_state.ahorro_actual = 0.0
    st.session_state.meta_ahorro = 500.0
    st.session_state.modo_demo = False

st.sidebar.caption("Los ejemplos son ficticios. Puedes desactivar el modo para empezar en blanco.")

if section == "🏠 Inicio":
    st.header("¡Bienvenido/a!")
    st.write("Elige una actividad. Puedes comenzar por cualquiera y avanzar a tu ritmo.")
    inc, exp, balance = totals()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Saldo de práctica", money(balance))
    c2.metric("🌱 Ahorro registrado", money(st.session_state.ahorro_actual))
    c3.metric("🎯 Meta de ahorro", money(st.session_state.meta_ahorro))
    st.subheader("Explora los módulos")
    cards = [
        ("🪙 Conocer el dinero", "Reconocer cantidades y practicar sumas."),
        ("🛍️ Practicar compras", "Elegir productos y calcular el cambio."),
        ("📊 Organizar mi dinero", "Registrar ingresos y gastos."),
        ("🌱 Ahorrar", "Crear una meta y observar el progreso."),
        ("🎮 Retos y juegos", "Resolver situaciones cotidianas."),
        ("💬 Ayuda FinanIA", "Consultar explicaciones sencillas."),
    ]
    cols = st.columns(3)
    for i, (title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="finania-card"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
    st.success("Puedes repetir las actividades todas las veces que quieras.")

elif section == "🪙 Conozco el dinero":
    st.header("🪙 Conozco el dinero")
    hint("Observa la tarjeta, elige la cantidad y presiona Comprobar.")
    examples = {
        "Una moneda de $5": 5, "Dos monedas de $10": 20,
        "Un billete de $20": 20, "Un billete de $50": 50,
        "Cinco monedas de $10": 50
    }
    item = st.selectbox("Observa esta representación:", list(examples.keys()))
    st.subheader("💵 " + item)
    answer = st.radio("¿Cuánto dinero representa?", [5, 10, 20, 30, 50, 100],
                      horizontal=True, key="money_answer")
    if st.button("Comprobar cantidad", key="check_money"):
        if answer == examples[item]:
            st.success("¡Correcto! Identificaste la cantidad. 🎉")
        else:
            st.warning("Vuelve a mirar la representación e inténtalo otra vez.")
    st.divider()
    st.subheader("➕ Practica una suma")
    a, b = st.columns(2)
    with a:
        first = st.selectbox("Primera cantidad", [1, 2, 5, 10, 20], key="sum_first")
    with b:
        second = st.selectbox("Segunda cantidad", [1, 2, 5, 10, 20], key="sum_second")
    result = st.number_input("Escribe el total", min_value=0, max_value=100, step=1, key="sum_result")
    if st.button("Revisar suma", key="check_sum"):
        if result == first + second:
            st.success(f"¡Muy bien! {first} + {second} = {first + second}.")
        else:
            st.info(f"Pista: empieza con {first} y agrega {second}.")

elif section == "🛍️ Practico compras":
    st.header("🛍️ Practico compras")
    hint("Selecciona un producto, revisa el precio y elige cuánto dinero entregas.")
    products = {"🍎 Manzana": 12, "🥛 Leche": 24, "🍞 Pan": 18,
                "📒 Cuaderno": 35, "🖍️ Colores": 42, "🧼 Jabón": 16}
    product = st.selectbox("¿Qué quieres comprar?", list(products.keys()))
    price = products[product]
    st.metric("Precio", money(price))
    paid = st.selectbox("¿Cuánto dinero entregas?", [10, 20, 50, 100, 200], index=2)
    if st.button("Calcular cambio", key="calculate_change"):
        if paid < price:
            st.error(f"Te faltan {money(price - paid)}.")
        else:
            st.success(f"Tu cambio sería {money(paid - price)}. ¡Buen trabajo!")
    st.caption("Simulación educativa: no realiza compras ni pagos reales.")

elif section == "📊 Organizo mi dinero":
    st.header("📊 Organizo mi dinero")
    hint("Completa los campos y presiona Guardar movimiento. Puedes usar datos ficticios.")
    with st.form("movement_form", clear_on_submit=True):
        kind = st.radio("Tipo de movimiento", ["Ingreso", "Gasto"], horizontal=True)
        concept = st.text_input("Concepto", placeholder="Ej. dinero para transporte")
        amount = st.number_input("Cantidad en pesos", min_value=0.0, step=1.0)
        category = st.selectbox("Categoría", [
            "Alimentación", "Transporte", "Educación", "Hogar",
            "Diversión", "Salud", "Ahorro", "Otro"
        ])
        submitted = st.form_submit_button("Guardar movimiento")
    if submitted:
        if amount <= 0:
            st.error("Escribe una cantidad mayor que cero.")
        else:
            add_movement(kind, concept.strip(), category, amount)
            st.success("¡Movimiento guardado en esta sesión!")
    inc, exp, balance = totals()
    a, b, c = st.columns(3)
    a.metric("Ingresos", money(inc))
    b.metric("Gastos", money(exp))
    c.metric("Diferencia", money(balance))
    if st.session_state.movimientos:
        st.subheader("Mis movimientos")
        st.dataframe(pd.DataFrame(st.session_state.movimientos), use_container_width=True, hide_index=True)
        if st.button("Borrar todos los movimientos", key="clear_movements"):
            st.session_state.movimientos = []
            st.rerun()
    else:
        st.info("Todavía no hay movimientos. Agrega uno de práctica para comenzar.")

elif section == "🌱 Mi ahorro":
    st.header("🌱 Mi ahorro")
    hint("Define una meta y registra cuánto llevas ahorrado.")
    goal = st.number_input("Mi meta de ahorro (pesos)", min_value=1.0,
                           value=float(st.session_state.meta_ahorro), step=10.0)
    saved = st.number_input("¿Cuánto llevo ahorrado? (pesos)", min_value=0.0,
                            value=float(st.session_state.ahorro_actual), step=5.0)
    st.session_state.meta_ahorro = goal
    st.session_state.ahorro_actual = saved
    progress = min(saved / goal, 1.0)
    st.progress(progress)
    st.write(f"Avance: **{progress * 100:.0f}%**")
    remaining = max(goal - saved, 0)
    if remaining == 0:
        st.success("¡Meta alcanzada! ¡Felicidades! 🎉")
    else:
        st.info(f"Te faltan {money(remaining)} para llegar a tu meta.")

elif section == "🎮 Retos y juegos":
    st.header("🎮 Retos y juegos")
    hint("Lee la situación, selecciona una respuesta y comprueba.")
    challenges = [
        ("Tienes $50 y compras algo que cuesta $30. ¿Cuánto queda?",
         ["$10", "$20", "$30"], "$20", "50 - 30 = 20. Quedan $20."),
        ("¿Cuál puede ser una necesidad básica?",
         ["Agua", "Videojuego", "Juguete"], "Agua", "El agua es necesaria para vivir."),
        ("Un producto cuesta $15. ¿Qué billete puede cubrir el precio?",
         ["$10", "$20", "$5"], "$20", "Con $20 pagas $15 y recibes $5."),
        ("Quieres ahorrar para una mochila. ¿Qué puede ayudarte?",
         ["Gastar todo hoy", "Guardar una parte", "No revisar el precio"],
         "Guardar una parte", "Guardar poco a poco ayuda a alcanzar una meta.")
    ]
    for idx, (question, options, correct, explanation) in enumerate(challenges, start=1):
        with st.container(border=True):
            st.markdown(f"**Reto {idx}**")
            st.write(question)
            choice = st.radio("Selecciona una respuesta:", options,
                              key=f"challenge_choice_{idx}", label_visibility="collapsed")
            if st.button("Comprobar respuesta", key=f"challenge_check_{idx}"):
                if choice == correct:
                    st.success("¡Respuesta correcta! 🌟 " + explanation)
                else:
                    st.warning("Puedes volver a intentarlo. Pista: " + explanation)

elif section == "💬 Ayuda FinanIA":
    st.header("💬 Ayuda FinanIA")
    st.write("Escribe una pregunta. Esta versión usa explicaciones educativas preparadas; no necesita una API.")
    question = st.text_input("¿Qué quieres aprender?", placeholder="Ej. ¿Qué significa ahorrar?")
    if st.button("Ver explicación", key="ask_finania"):
        q = question.lower().strip()
        answers = [
            (["ahorrar", "ahorro"], "Ahorrar significa guardar una parte del dinero para utilizarla después. Puedes elegir una meta y avanzar poco a poco."),
            (["cambio", "vuelto"], "El cambio es el dinero que recibes cuando entregas más de lo que cuesta un producto. Resta: dinero entregado menos precio."),
            (["presupuesto", "organizar"], "Un presupuesto es un plan para organizar el dinero que recibes y decidir cómo utilizarlo."),
            (["necesidad", "deseo"], "Una necesidad es algo importante para vivir o estar bien, como alimentos o agua. Un deseo es algo que te gustaría tener, pero puede esperar."),
            (["precio", "comparar"], "Para comparar precios, observa cuánto cuesta cada opción y qué cantidad o características ofrece.")
        ]
        reply = next((text for words, text in answers if any(word in q for word in words)), None)
        if reply:
            st.success(reply)
        elif q:
            st.info("Puedo explicar: ahorro, cambio, presupuesto, necesidades, deseos y comparación de precios.")
        else:
            st.warning("Escribe una pregunta o una palabra sobre el tema.")
    st.caption("Este asistente básico no es un chatbot generativo y no envía preguntas a internet.")

elif section == "⚙️ Mi experiencia":
    st.header("⚙️ Mi experiencia")
    st.write("Adapta la aplicación a tus preferencias.")
    st.session_state.nombre = st.text_input("Nombre o apodo (opcional)", value=st.session_state.nombre)
    st.session_state.tamano_letra = st.select_slider(
        "Tamaño de letra", options=["Pequeña", "Mediana", "Grande", "Muy grande"],
        value=st.session_state.tamano_letra
    )
    st.session_state.alto_contraste = st.toggle("Activar alto contraste", value=st.session_state.alto_contraste)
    st.session_state.mostrar_pistas = st.toggle(
        "Mostrar instrucciones paso a paso", value=st.session_state.mostrar_pistas
    )
    st.success("Tus preferencias se aplican durante esta sesión.")
    st.caption("Cada persona tiene preferencias diferentes. Puedes cambiar los ajustes cuando quieras.")

st.divider()
st.caption(
    "FinanIA Inclusivo · Herramienta educativa. No ofrece asesoría financiera, "
    "no realiza pagos y no diagnostica. Utiliza datos ficticios o de práctica."
)
