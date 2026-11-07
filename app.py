import sqlite3
from datetime import date
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

DB = "finania.db"
CATEGORIES = ["Alimentación", "Transporte", "Salud", "Educación", "Hogar", "Entretenimiento", "Ropa", "Otros"]

# Pequeño conjunto de ejemplos para una demostración educativa.
# En un proyecto real debe ampliarse y validarse con datos diversos.
TRAIN_TEXTS = [
    "tacos comida restaurante supermercado pan leche fruta verduras",
    "gasolina camión autobús taxi tren transporte estacionamiento",
    "medicina farmacia consulta doctor hospital lentes",
    "libro escuela curso cuaderno lápiz colegiatura educación",
    "renta luz agua internet gas muebles limpieza hogar",
    "cine videojuegos concierto paseo música streaming diversión",
    "zapatos pantalón camisa vestido chamarra ropa",
    "regalo reparación varios otro"
]
TRAIN_LABELS = ["Alimentación", "Transporte", "Salud", "Educación",
                "Hogar", "Entretenimiento", "Ropa", "Otros"]

@st.cache_resource
def build_model():
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("classifier", MultinomialNB())
    ])
    model.fit(TRAIN_TEXTS, TRAIN_LABELS)
    return model

def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            day TEXT NOT NULL
        )
    """)
    con.commit()
    return con

con = connect()
model = build_model()

st.set_page_config(page_title="FinanIA Inclusivo", page_icon="🧩", layout="centered")

st.sidebar.title("Ajustes de accesibilidad")
font_choice = st.sidebar.selectbox("Tamaño del texto", ["Normal", "Grande", "Muy grande"])
st.sidebar.caption("Puedes cambiar estas opciones cuando quieras.")
font_sizes = {"Normal": "17px", "Grande": "20px", "Muy grande": "24px"}
st.markdown(f"""
<style>
html, body, [class*="st-"] {{ font-size: {font_sizes[font_choice]}; }}
.stButton button, .stSelectbox, .stTextInput, .stNumberInput {{
    min-height: 3rem;
}}
.block-container {{ max-width: 900px; padding-top: 2rem; }}
</style>
""", unsafe_allow_html=True)

st.title("🧩 FinanIA Inclusivo")
st.subheader("Aprende a organizar tu dinero paso a paso")
st.write("Una herramienta educativa configurable. No necesitas conectar cuentas bancarias.")

tab_home, tab_add, tab_learn, tab_data = st.tabs(
    ["Mi resumen", "Registrar movimiento", "Aprender", "Mis movimientos"]
)

with tab_home:
    rows = con.execute("SELECT kind, amount, category FROM transactions").fetchall()
    df = pd.DataFrame(rows, columns=["Tipo", "Cantidad", "Categoría"])
    income = df.loc[df["Tipo"] == "Ingreso", "Cantidad"].sum() if not df.empty else 0
    expenses = df.loc[df["Tipo"] == "Gasto", "Cantidad"].sum() if not df.empty else 0
    balance = income - expenses
    c1, c2 = st.columns(2)
    c1.metric("Ingresos registrados", f"${income:,.2f} MXN")
    c2.metric("Gastos registrados", f"${expenses:,.2f} MXN")
    st.metric("Diferencia", f"${balance:,.2f} MXN")
    if not df.empty:
        spend = df[df["Tipo"] == "Gasto"].groupby("Categoría")["Cantidad"].sum()
        if not spend.empty:
            st.write("### Gastos por categoría")
            st.bar_chart(spend)
    st.info("Los datos se guardan localmente en el archivo finania.db de esta computadora.")

with tab_add:
    st.write("### Agrega un ingreso o gasto")
    with st.form("transaction_form"):
        kind = st.radio("¿Qué quieres registrar?", ["Gasto", "Ingreso"], horizontal=True)
        description = st.text_input("¿En qué fue? (por ejemplo: comida, camión, libro)")
        amount = st.number_input("Cantidad en pesos", min_value=0.01, value=50.00, step=10.00)
        day = st.date_input("Fecha", value=date.today())
        predicted = model.predict([description])[0] if description.strip() else "Otros"
        st.write(f"Categoría sugerida por IA: **{predicted}**")
        category = st.selectbox("Confirma o cambia la categoría", CATEGORIES,
                                index=CATEGORIES.index(predicted) if predicted in CATEGORIES else 0)
        submitted = st.form_submit_button("Guardar movimiento")
        if submitted:
            if not description.strip():
                st.error("Escribe una descripción breve.")
            else:
                con.execute(
                    "INSERT INTO transactions(kind, description, amount, category, day) VALUES(?,?,?,?,?)",
                    (kind, description.strip(), float(amount), category, day.isoformat())
                )
                con.commit()
                st.success("Movimiento guardado.")
                st.rerun()

with tab_learn:
    st.write("### Practica con situaciones cotidianas")
    st.write("Puedes repetir la actividad o cambiar los números.")
    st.write("**Situación:** Tienes $200. Compras un cuaderno que cuesta $65.")
    if st.button("Mostrar explicación"):
        st.success("Te quedan $135, porque $200 − $65 = $135.")
    st.divider()
    st.write("### Mi meta de ahorro")
    goal = st.number_input("¿Cuánto quieres ahorrar? (MXN)", min_value=1.0, value=500.0, step=50.0)
    saved = st.number_input("¿Cuánto has ahorrado? (MXN)", min_value=0.0, value=100.0, step=10.0)
    progress = min(saved / goal, 1.0)
    st.progress(progress)
    st.write(f"Has ahorrado ${saved:,.2f} de ${goal:,.2f}.")
    st.write(f"Te faltan ${max(goal-saved, 0):,.2f} para alcanzar tu meta.")

with tab_data:
    st.write("### Historial de movimientos")
    data = con.execute(
        "SELECT day AS Fecha, kind AS Tipo, description AS Descripción, category AS Categoría, amount AS Cantidad "
        "FROM transactions ORDER BY day DESC"
    ).fetchall()
    history = pd.DataFrame(data, columns=["Fecha", "Tipo", "Descripción", "Categoría", "Cantidad"])
    if history.empty:
        st.info("Todavía no hay movimientos. Registra uno en la pestaña anterior.")
    else:
        st.dataframe(history, use_container_width=True, hide_index=True)
        if st.button("Borrar todos mis movimientos"):
            con.execute("DELETE FROM transactions")
            con.commit()
            st.success("Historial borrado.")
            st.rerun()

st.divider()
st.caption(
    "FinanIA es un prototipo educativo. La clasificación automática es experimental y puede equivocarse; "
    "por eso puedes revisar y corregir cada categoría. No ofrece asesoría financiera ni realiza pagos."
)
