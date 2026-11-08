
import streamlit as st
import pandas as pd
from datetime import date
import random

st.set_page_config(page_title="FinanIA Inclusivo", page_icon="💜", layout="wide")

# ---------- Estado ----------
defaults = {
    "movimientos": [],
    "meta_nombre": "Mi primera meta",
    "meta_total": 500.0,
    "meta_actual": 0.0,
    "letra": "Mediana",
    "contraste": "Suave",
    "instrucciones": True,
    "edad": "Prefiero elegir mis actividades",
    "nombre": "",
    "reto_puntos": 0,
    "retos_completados": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- Estilos ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
:root { --ink:#27304b; --muted:#68718a; --purple:#6c4bd8; --pink:#f4a7c4; --mint:#a8e6cf; --yellow:#ffe49a; }
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px;}
.hero {
 background: linear-gradient(120deg,#eee8ff 0%,#fff0f5 52%,#e6fbf4 100%);
 border: 1px solid #e7ddff; border-radius: 26px; padding: 28px 30px; margin-bottom: 18px;
}
.hero h1 {color:#39276f; font-size:2.25rem; margin:0 0 8px 0; font-weight:900;}
.hero p {color:#4f5670; font-size:1.08rem; margin:0;}
.card {
 background:#ffffff; border:1px solid #e9e8f2; border-radius:20px; padding:18px 20px;
 box-shadow:0 4px 14px rgba(54,44,100,.05); min-height:120px;
}
.card h3 {margin:0 0 6px 0; color:#34265f; font-size:1.12rem;}
.card p {margin:0; color:#68718a;}
.pill {display:inline-block; padding:5px 11px; border-radius:99px; background:#f0ebff; color:#5639b5; font-weight:800; font-size:.82rem;}
.small-muted {color:#68718a; font-size:.92rem;}
div.stButton > button {border-radius:14px; min-height:2.8rem; font-weight:800; border:1px solid #d9d1f5;}
div.stButton > button[kind="primary"] {background:#6c4bd8; color:white; border:0;}
div[data-testid="stMetric"] {background:#fbfaff; border:1px solid #ece7fb; padding:14px; border-radius:16px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f5f1ff,#fff8fb);}
h1,h2,h3 {color:#34265f;}
</style>
""", unsafe_allow_html=True)

if st.session_state.contraste == "Alto":
    st.markdown("""<style>
    .card {border:2px solid #34304a; box-shadow:none;}
    .hero {border:2px solid #34304a;}
    p, label, .small-muted {color:#202033 !important;}
    </style>""", unsafe_allow_html=True)

font_css = {"Pequeña":"16px", "Mediana":"18px", "Grande":"21px", "Muy grande":"24px"}[st.session_state.letra]
st.markdown(f"<style>html, body, [class*='css'] {{font-size:{font_css};}}</style>", unsafe_allow_html=True)

# ---------- Utilidades ----------
def money(n):
    return f"${n:,.2f}"

def hero(title, subtitle, emoji="💜"):
    st.markdown(f"""
    <div class="hero">
      <div style="font-size:2.2rem">{emoji}</div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>""", unsafe_allow_html=True)

def card(title, desc, emoji):
    st.markdown(f"""<div class="card"><div style="font-size:2rem">{emoji}</div>
    <h3>{title}</h3><p>{desc}</p></div>""", unsafe_allow_html=True)

def hint(text):
    if st.session_state.instrucciones:
        st.info("💡 **Paso a paso:** " + text)

# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("## 💜 FinanIA")
    st.caption("Aprendo sobre el dinero a mi ritmo")
    if st.session_state.nombre:
        st.write(f"¡Hola, {st.session_state.nombre}!")
    page = st.radio(
        "¿A dónde quieres ir?",
        ["🏠 Inicio", "🪙 Conozco el dinero", "🛍️ Practico compras",
         "📊 Organizo mi dinero", "🌱 Mi ahorro", "🎮 Retos y juegos", "⚙️ Mi experiencia"],
        label_visibility="visible"
    )
    st.divider()
    st.caption("Puedes cambiar de sección cuando quieras.")
    st.caption("No hay límite de tiempo. Puedes repetir las actividades.")

# ---------- Inicio ----------
if page == "🏠 Inicio":
    hero("¡Bienvenido a FinanIA!", "Un espacio para aprender a usar el dinero, tomar decisiones y avanzar a tu propio ritmo.", "🌈")
    c1, c2 = st.columns([1.4,1])
    with c1:
        st.subheader("¿Qué te gustaría aprender hoy?")
        st.write("Elige una actividad. No necesitas hacerlas todas ni seguir un orden.")
        a,b = st.columns(2)
        with a:
            card("Conocer el dinero","Identifica monedas, billetes y cantidades.","🪙")
            card("Practicar compras","Simula compras y calcula el cambio.","🛍️")
            card("Organizar mi dinero","Registra entradas, gastos y revisa tu saldo.","📊")
        with b:
            card("Aprender a ahorrar","Crea una meta y observa tu progreso.","🌱")
            card("Jugar y practicar","Resuelve pequeños retos financieros.","🎮")
            card("Personalizar","Ajusta letra, contraste e instrucciones.","⚙️")
    with c2:
        st.subheader("Mi resumen")
        ingresos = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"]=="Ingreso")
        gastos = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"]=="Gasto")
        st.metric("Dinero que tengo registrado", money(ingresos-gastos))
        st.metric("Retos completados", len(st.session_state.retos_completados))
        st.metric("Progreso de ahorro", f"{min(100, st.session_state.meta_actual/max(st.session_state.meta_total,1)*100):.0f}%")
        st.markdown('<div class="card"><h3>🌟 Recuerda</h3><p>Aprender lleva tiempo. Puedes pedir ayuda, descansar o volver a intentar cuando quieras.</p></div>', unsafe_allow_html=True)
    st.caption("FinanIA es una herramienta educativa. Utiliza cantidades de ejemplo; no conecta con bancos ni realiza pagos.")

# ---------- Dinero ----------
elif page == "🪙 Conozco el dinero":
    hero("Conozco el dinero", "Vamos a reconocer cantidades y practicar sumas sencillas.", "🪙")
    hint("Lee cada pregunta. Elige una respuesta y comprueba cómo te fue.")
    st.subheader("Actividad 1. ¿Cuánto dinero hay?")
    st.write("Imagina que tienes una moneda de $10 y otra de $5.")
    answer = st.radio("¿Cuánto dinero tienes en total?", ["$5", "$10", "$15", "$20"], key="dinero_q1")
    if st.button("Comprobar respuesta", key="check_money"):
        if answer == "$15":
            st.success("¡Correcto! $10 + $5 = $15. ¡Buen trabajo!")
        else:
            st.warning("No pasa nada. Inténtalo otra vez: suma 10 y 5.")
    st.divider()
    st.subheader("Actividad 2. Completa la cantidad")
    x = st.selectbox("Tienes $20. ¿Cuánto falta para llegar a $50?", ["Selecciona", "$10", "$20", "$30", "$40"], key="dinero_q2")
    if st.button("Revisar", key="check_money2"):
        if x == "$30": st.success("¡Así es! $20 + $30 = $50.")
        else: st.info("Pista: piensa cuánto hay entre 20 y 50.")

# ---------- Compras ----------
elif page == "🛍️ Practico compras":
    hero("Practico compras", "Haz una compra de práctica. Aquí no se utiliza dinero real.", "🛍️")
    hint("Elige un producto, observa su precio y escribe cuánto dinero entregas.")
    products = {"🍎 Manzana": 12, "🥪 Sándwich": 35, "📒 Cuaderno": 28, "🧃 Jugo": 18, "🧸 Pelota": 65}
    product = st.selectbox("¿Qué quieres comprar?", list(products.keys()))
    price = products[product]
    st.markdown(f'<div class="card"><h3>{product}</h3><p>Precio de práctica</p><div style="font-size:2rem;font-weight:900;color:#6c4bd8">{money(price)}</div></div>', unsafe_allow_html=True)
    paid = st.number_input("¿Cuánto dinero entregas?", min_value=0, max_value=1000, value=50, step=5)
    if st.button("Calcular mi cambio", type="primary"):
        if paid < price:
            st.warning(f"Te faltan {money(price-paid)} para pagar.")
        else:
            st.success(f"Tu cambio es {money(paid-price)}. ¡Compra completada!")
    st.caption("Los precios son ejemplos para practicar.")

# ---------- Administración ----------
elif page == "📊 Organizo mi dinero":
    hero("Organizo mi dinero", "Registra movimientos de ejemplo y observa cómo cambia tu saldo.", "📊")
    hint("Selecciona si recibiste dinero o si gastaste. Después completa la descripción y la cantidad.")
    with st.form("movement_form", clear_on_submit=True):
        tipo = st.radio("Tipo de movimiento", ["Ingreso","Gasto"], horizontal=True)
        desc = st.text_input("¿Qué ocurrió?", placeholder="Ej. Recibí dinero para transporte")
        cantidad = st.number_input("Cantidad en pesos", min_value=0.0, value=0.0, step=10.0)
        categoria = st.selectbox("Categoría", ["Alimentación","Transporte","Escuela","Hogar","Diversión","Regalo","Trabajo","Otro"])
        submitted = st.form_submit_button("Guardar movimiento", type="primary")
        if submitted:
            if not desc.strip() or cantidad <= 0:
                st.error("Escribe una descripción y una cantidad mayor que cero.")
            else:
                st.session_state.movimientos.append({"fecha":str(date.today()),"tipo":tipo,"descripcion":desc.strip(),"categoria":categoria,"cantidad":float(cantidad)})
                st.success("Movimiento agregado a esta sesión.")
    ingresos = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"]=="Ingreso")
    gastos = sum(x["cantidad"] for x in st.session_state.movimientos if x["tipo"]=="Gasto")
    m1,m2,m3 = st.columns(3)
    m1.metric("Ingresos",money(ingresos)); m2.metric("Gastos",money(gastos)); m3.metric("Saldo",money(ingresos-gastos))
    if st.session_state.movimientos:
        df = pd.DataFrame(st.session_state.movimientos)
        st.subheader("Mis movimientos")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.groupby("tipo")["cantidad"].sum())
        if st.button("Borrar movimientos de esta sesión"):
            st.session_state.movimientos = []
            st.rerun()
    else:
        st.info("Todavía no hay movimientos. Agrega uno para comenzar.")

# ---------- Ahorro ----------
elif page == "🌱 Mi ahorro":
    hero("Mi meta de ahorro", "Cada pequeño paso cuenta. Tú decides cuánto quieres reunir.", "🌱")
    hint("Escribe el nombre de tu meta y la cantidad que quieres ahorrar. Luego agrega lo que llevas.")
    with st.form("goal_form"):
        name = st.text_input("¿Para qué quieres ahorrar?", value=st.session_state.meta_nombre)
        total = st.number_input("¿Cuánto quieres reunir? ($)", min_value=1.0, value=float(st.session_state.meta_total), step=50.0)
        actual = st.number_input("¿Cuánto has ahorrado? ($)", min_value=0.0, value=float(st.session_state.meta_actual), step=10.0)
        save = st.form_submit_button("Actualizar mi meta", type="primary")
        if save:
            st.session_state.meta_nombre=name or "Mi meta"
            st.session_state.meta_total=total
            st.session_state.meta_actual=actual
            st.success("¡Meta actualizada!")
    total = max(float(st.session_state.meta_total),1)
    current = float(st.session_state.meta_actual)
    pct = min(1.0,current/total)
    st.subheader(st.session_state.meta_nombre)
    st.progress(pct)
    st.markdown(f"**Llevas {money(current)} de {money(total)} ({pct*100:.0f}%).**")
    st.info(f"Te faltan {money(max(0,total-current))} para alcanzar tu meta.")

# ---------- Retos ----------
elif page == "🎮 Retos y juegos":
    hero("Retos y juegos", "Practica con situaciones cotidianas. Puedes intentarlo todas las veces que quieras.", "🎮")
    hint("Lee el reto, elige una respuesta y presiona comprobar.")
    challenges = [
        ("Tienes $100 y gastas $40. ¿Cuánto queda?", ["$40","$50","$60"], "$60", "100 - 40 = 60."),
        ("Una libreta cuesta $25. Pagas con $50. ¿Cuál es el cambio?", ["$15","$25","$35"], "$25", "50 - 25 = 25."),
        ("Quieres ahorrar $100. Ya tienes $70. ¿Cuánto falta?", ["$20","$30","$40"], "$30", "100 - 70 = 30."),
        ("Un producto cuesta $45 y otro $39. ¿Cuál cuesta menos?", ["El de $45","El de $39","Cuestan igual"], "El de $39", "39 es menor que 45.")
    ]
    idx = st.selectbox("Elige un reto", list(range(1,len(challenges)+1)), format_func=lambda x:f"Reto {x}")
    q, opts, correct, explain = challenges[idx-1]
    st.markdown(f'<div class="card"><span class="pill">RETO {idx}</span><h3 style="margin-top:12px">{q}</h3></div>', unsafe_allow_html=True)
    response = st.radio("Tu respuesta",opts,key=f"challenge_{idx}")
    if st.button("Comprobar reto",type="primary"):
        if response == correct:
            st.success("¡Muy bien! " + explain)
            if idx not in st.session_state.retos_completados:
                st.session_state.retos_completados.append(idx)
                st.session_state.reto_puntos += 1
        else:
            st.warning("Puedes volver a intentarlo. Pista: " + explain)
    st.metric("Retos resueltos",f"{len(st.session_state.retos_completados)} de {len(challenges)}")
    st.caption("Los puntos son una forma de reconocer la práctica, no una calificación.")

# ---------- Preferencias ----------
elif page == "⚙️ Mi experiencia":
    hero("Mi experiencia", "Ajusta la aplicación para que sea más cómoda para ti.", "⚙️")
    st.subheader("Ajustes de lectura")
    st.session_state.letra = st.radio("Tamaño de letra",["Pequeña","Mediana","Grande","Muy grande"],index=["Pequeña","Mediana","Grande","Muy grande"].index(st.session_state.letra),horizontal=True)
    st.session_state.contraste = st.radio("Contraste",["Suave","Alto"],index=["Suave","Alto"].index(st.session_state.contraste),horizontal=True)
    st.session_state.instrucciones = st.toggle("Mostrar instrucciones paso a paso",value=st.session_state.instrucciones)
    st.subheader("Preferencias de aprendizaje")
    st.session_state.edad = st.selectbox("¿Qué opción describe mejor lo que buscas?",["Prefiero elegir mis actividades","Actividades para niñas y niños","Actividades para adolescentes","Actividades para personas adultas"],index=["Prefiero elegir mis actividades","Actividades para niñas y niños","Actividades para adolescentes","Actividades para personas adultas"].index(st.session_state.edad))
    st.text_input("¿Cómo te gustaría que te llamemos? (opcional)",key="nombre")
    st.success("Tus ajustes se aplican durante esta sesión.")
    st.caption("Puedes cambiar estas opciones en cualquier momento. No hay una única forma correcta de aprender.")

st.divider()
st.markdown("<div style='text-align:center;color:#77718b;font-size:.9rem'>💜 FinanIA Inclusivo · Aprende a tu ritmo · Prototipo educativo</div>", unsafe_allow_html=True)
