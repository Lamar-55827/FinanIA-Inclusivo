import random
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="KikiPay Inclusivo",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SECCIONES = [
    ("🏠 Inicio", "🏠", "Inicio"),
    ("🪙 Conozco el dinero", "🪙", "Dinero"),
    ("🛍️ Practico compras", "🛍️", "Compras"),
    ("📊 Organizo mi dinero", "📊", "Organizar"),
    ("🌱 Mi ahorro", "🌱", "Ahorro"),
    ("🎮 Retos y juegos", "🎮", "Retos"),
    ("💬 Ayuda KikiPay", "💬", "Ayuda"),
    ("⚙️ Mi experiencia", "⚙️", "Ajustes"),
]

DEFAULTS = {
    "seccion_actual": "🏠 Inicio",
    "movimientos": [],
    "meta_ahorro": 500.0,
    "ahorro_actual": 0.0,
    "nombre": "",
    "tamano_letra": "Mediana",
    "alto_contraste": False,
    "mostrar_pistas": True,
    "modo_demo": False,
    "reto_i": 0,
    "reto_intentos": 0,
    "reto_feedback": None,
    "reto_estrellas": {},
    "reto_puntos": 0,
    "reto_celebrado": False,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def ir_a(seccion):
    st.session_state.seccion_actual = seccion


# ---------------------------------------------------------------
# Patrón SVG de fondo: niños, jóvenes, adultos, números y letras
# ---------------------------------------------------------------
BG_PATTERN_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="520" height="520" viewBox="0 0 520 520">
  <g font-family="sans-serif" font-weight="900" opacity="0.22">
    <!-- Letras y Números flotantes -->
    <text x="35" y="65" font-size="38" fill="#FF4D8D" transform="rotate(-12 35 65)">A</text>
    <text x="235" y="55" font-size="34" fill="#7C4DFF" transform="rotate(10 235 55)">1 2 3</text>
    <text x="435" y="75" font-size="40" fill="#00B894" transform="rotate(-8 435 75)">B</text>
    <text x="145" y="165" font-size="36" fill="#FF8A00" transform="rotate(15 145 165)">$10</text>
    <text x="345" y="185" font-size="38" fill="#29B6F6" transform="rotate(-14 345 185)">C</text>
    <text x="45" y="295" font-size="36" fill="#8E24AA" transform="rotate(8 45 295)">5 + 5</text>
    <text x="265" y="305" font-size="42" fill="#FF4D8D" transform="rotate(-10 265 305)">Ñ</text>
    <text x="450" y="315" font-size="34" fill="#FF8A00" transform="rotate(12 450 315)">$20</text>
    <text x="140" y="445" font-size="38" fill="#00B894" transform="rotate(-12 140 445)">7</text>
    <text x="360" y="455" font-size="36" fill="#7C4DFF" transform="rotate(10 360 455)">ABC</text>
    <text x="470" y="485" font-size="32" fill="#E53935">100%</text>
  </g>

  <g opacity="0.26">
    <!-- Niño sonriendo (arriba izquierda) -->
    <g transform="translate(80, 95)">
      <circle cx="30" cy="24" r="16" fill="#FFB74D"/>
      <path d="M14 20 Q30 2 46 20" fill="#4E342E"/>
      <circle cx="24" cy="23" r="2.2" fill="#263238"/>
      <circle cx="36" cy="23" r="2.2" fill="#263238"/>
      <path d="M24 30 Q30 36 36 30" stroke="#263238" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <rect x="14" y="42" width="32" height="30" rx="12" fill="#29B6F6"/>
      <text x="30" y="62" font-size="14" font-weight="bold" fill="#FFF" text-anchor="middle">123</text>
    </g>

    <!-- Joven con lentes (arriba derecha) -->
    <g transform="translate(350, 75)">
      <circle cx="35" cy="26" r="18" fill="#D7CCC8"/>
      <path d="M15 24 Q18 4 35 6 Q52 4 55 24 L55 38 L15 38 Z" fill="#3E2723"/>
      <circle cx="35" cy="27" r="17" fill="#F5CBA7"/>
      <circle cx="28" cy="26" r="5" stroke="#7C4DFF" stroke-width="2.2" fill="none"/>
      <circle cx="42" cy="26" r="5" stroke="#7C4DFF" stroke-width="2.2" fill="none"/>
      <line x1="33" y1="26" x2="37" y2="26" stroke="#7C4DFF" stroke-width="2"/>
      <path d="M29 34 Q35 39 41 34" stroke="#263238" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <rect x="16" y="46" width="38" height="36" rx="14" fill="#FF4D8D"/>
    </g>

    <!-- Adulto mayor feliz (centro izquierda) -->
    <g transform="translate(175, 225)">
      <circle cx="35" cy="28" r="19" fill="#ECEFF1"/>
      <circle cx="35" cy="30" r="17" fill="#FFCCBC"/>
      <circle cx="29" cy="28" r="2.2" fill="#263238"/>
      <circle cx="41" cy="28" r="2.2" fill="#263238"/>
      <path d="M28 36 Q35 42 42 36" stroke="#263238" stroke-width="2.3" fill="none" stroke-linecap="round"/>
      <rect x="14" y="49" width="42" height="38" rx="15" fill="#00B894"/>
    </g>

    <!-- Niña con coletas (centro derecha) -->
    <g transform="translate(385, 230)">
      <circle cx="15" cy="20" r="8" fill="#5D4037"/>
      <circle cx="55" cy="20" r="8" fill="#5D4037"/>
      <circle cx="35" cy="26" r="16" fill="#8D5524"/>
      <circle cx="29" cy="25" r="2.2" fill="#FFF"/>
      <circle cx="41" cy="25" r="2.2" fill="#FFF"/>
      <path d="M29 32 Q35 37 41 32" stroke="#FFF" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <rect x="18" y="44" width="34" height="30" rx="12" fill="#FFB300"/>
    </g>

    <!-- Adulto joven (abajo izquierda) -->
    <g transform="translate(55, 375)">
      <circle cx="35" cy="26" r="18" fill="#F8C471"/>
      <path d="M17 22 Q35 4 53 22" fill="#1B2631"/>
      <circle cx="29" cy="26" r="2.2" fill="#263238"/>
      <circle cx="41" cy="26" r="2.2" fill="#263238"/>
      <path d="M29 34 Q35 39 41 34" stroke="#263238" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <rect x="15" y="46" width="40" height="38" rx="14" fill="#7C4DFF"/>
    </g>

    <!-- Monedas, estrellas y alcancía -->
    <circle cx="275" cy="125" r="18" fill="#FFD54F" stroke="#FF8F00" stroke-width="3"/>
    <text x="275" y="131" font-size="18" font-weight="900" fill="#E65100" text-anchor="middle">$</text>

    <circle cx="260" cy="400" r="20" fill="#FFD54F" stroke="#FF8F00" stroke-width="3"/>
    <text x="260" y="407" font-size="20" font-weight="900" fill="#E65100" text-anchor="middle">$5</text>

    <polygon points="465,160 470,173 484,173 473,181 477,194 465,186 453,194 457,181 446,173 460,173" fill="#FFB300"/>
    <polygon points="115,215 119,225 130,225 121,231 124,242 115,235 106,242 109,231 100,225 111,225" fill="#FF4D8D"/>
  </g>
</svg>
"""
BG_PATTERN_URI = "data:image/svg+xml;utf8," + urllib.parse.quote(BG_PATTERN_SVG)

font_sizes = {"Pequeña": 16, "Mediana": 18, "Grande": 21, "Muy grande": 24}
font_px = font_sizes[st.session_state.tamano_letra]
HC = st.session_state.alto_contraste

if HC:
    app_bg = "#101820"
    fg, card, border = "#FFFFFF", "#202D38", "#FFFFFF"
    btn_bg, btn_fg = "#FFD600", "#000000"
    main_container_bg = "rgba(16, 24, 32, 0.96)"
else:
    app_bg = (
        f'url("{BG_PATTERN_URI}"), '
        "linear-gradient(135deg,#FFE3F1 0%,#E4EEFF 30%,#DDFBF0 60%,#FFF3C9 100%)"
    )
    fg, card, border = "#263238", "#FFFFFF", "#CBB8FF"
    btn_bg, btn_fg = "linear-gradient(135deg,#7C4DFF,#00B8A9)", "#FFFFFF"
    main_container_bg = "rgba(255, 255, 255, 0.78)"

st.markdown(
    f"""
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none !important; }}
.stApp {{
  background: {app_bg};
  background-repeat: repeat, no-repeat;
  background-size: 460px 460px, cover;
  background-attachment: fixed;
  color: {fg};
}}
html, body, [class*="st-"], p, label, li {{ font-size: {font_px}px; }}
.block-container {{
  max-width: 1180px;
  padding-top: 1.4rem;
  padding-bottom: 3rem;
  background: {main_container_bg};
  border-radius: 28px;
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 35px rgba(108, 92, 231, 0.14);
  backdrop-filter: blur(4px);
}}
.kikipay-hero {{
  position: relative;
  overflow: hidden;
  background: linear-gradient(120deg,#FF4D8D 0%,#FF8A00 35%,#00B894 70%,#6C5CE7 100%);
  color:#FFFFFF;
  padding: 1.7rem 2rem;
  border-radius: 26px;
  margin-bottom: 1rem;
  border: 4px solid #FFFFFF;
  box-shadow: 0 10px 26px rgba(108,92,231,.38);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}}
.kikipay-hero-text {{
  flex: 1 1 520px;
  z-index: 2;
}}
.kikipay-title {{
  font-size: clamp(2.3rem, 4.6vw, 3.6rem) !important;
  font-weight: 900 !important;
  line-height: 1.08 !important;
  letter-spacing: -0.5px;
  color: #FFFFFF !important;
  margin: 0 0 0.45rem 0 !important;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.35), 0 0 22px rgba(255, 255, 255, 0.35);
}}
.kikipay-hero h3 {{
  font-size: clamp(1.15rem, 2vw, 1.45rem) !important;
  font-weight: 700 !important;
  color: #FFFDE7 !important;
  margin: 0.25rem 0 !important;
  text-shadow: 0 2px 5px rgba(0,0,0,.28);
}}
.kikipay-hero p {{
  color: #FFFFFF !important;
  margin: 0.35rem 0 0 0 !important;
  font-weight: 500;
  text-shadow: 0 1px 4px rgba(0,0,0,.28);
}}
.kikipay-hero-art {{
  flex: 0 1 330px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2;
}}
[data-testid="stMetric"] {{
  background:{card}; border:2px solid {border};
  border-left: 10px solid #FF6B9D; border-radius:16px; padding:.8rem 1rem;
  box-shadow: 0 3px 10px rgba(0,0,0,.08);
}}
div.stButton > button, div.stFormSubmitButton > button {{
  min-height: 3.4rem; border-radius: 18px; font-weight: 800; border: none;
  background: {btn_bg}; color: {btn_fg}; box-shadow: 0 4px 10px rgba(0,0,0,.18);
  transition: transform .15s, filter .15s; padding: 0.55rem 0.6rem;
  white-space: pre-line !important; line-height: 1.25 !important;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
  transform: scale(1.03); filter: brightness(1.08);
}}
div.stButton > button p {{
  color: {btn_fg}; font-size: {font_px + 1}px !important;
  white-space: pre-line !important; overflow: visible !important; text-overflow: unset !important;
}}
.reto-card {{ border-radius:20px; padding:1.1rem 1.3rem; border:4px solid; margin:.5rem 0; }}
.score-row {{ display:flex; gap:.7rem; flex-wrap:wrap; margin:.3rem 0 .6rem; }}
.score {{
  flex:1; min-width:140px; border-radius:16px; padding:.6rem .9rem;
  color:#fff; font-weight:700; text-align:center; text-shadow:0 1px 3px rgba(0,0,0,.35);
}}
.path {{ display:flex; gap:.5rem; flex-wrap:wrap; margin:.4rem 0 .8rem; }}
.chip {{
  flex:1; min-width:110px; text-align:center; border-radius:999px; padding:.45rem .6rem;
  font-weight:700; color:#fff; text-shadow:0 1px 2px rgba(0,0,0,.35);
}}
</style>
""",
    unsafe_allow_html=True,
)


def md_safe(text):
    return str(text).replace("$", "\\$")


def header(text):
    st.header(md_safe(text))


def subheader(text):
    st.subheader(md_safe(text))


def msg(kind, text):
    getattr(st, kind)(md_safe(text))


def prompt(text):
    st.markdown("**" + md_safe(text) + "**")


def hint(message):
    if st.session_state.mostrar_pistas:
        msg("info", "**Paso a paso:** " + message)


def money(value):
    return f"${value:,.2f} MXN"


def totals():
    income = sum(x["Cantidad"] for x in st.session_state.movimientos if x["Tipo"] == "Ingreso")
    expense = sum(x["Cantidad"] for x in st.session_state.movimientos if x["Tipo"] == "Gasto")
    return income, expense, income - expense


def add_movement(kind, concept, category, amount):
    st.session_state.movimientos.append({
        "Fecha": str(date.today()),
        "Tipo": kind,
        "Concepto": concept or category,
        "Categoría": category,
        "Cantidad": float(amount),
    })


NIVELES = {
    1: ("🌱", "Muy fácil", "#43A047", "#E3F6E4"),
    2: ("🌿", "Fácil", "#00ACC1", "#DDF5F9"),
    3: ("🌳", "Medio", "#FB8C00", "#FFEFD9"),
    4: ("🌟", "Difícil", "#E53935", "#FFE3E2"),
    5: ("🏆", "Experto", "#8E24AA", "#F3E1F8"),
}

RETOS = [
    {"nivel": 1, "q": "¿Cuánto vale una moneda de $10?", "op": ["$5", "$10", "$20"], "ok": "$10", "exp": "La moneda dice 10, así que vale $10."},
    {"nivel": 1, "q": "¿Cuál de estas cosas sirve para pagar?", "op": ["Una nube", "Dinero", "Un lápiz"], "ok": "Dinero", "exp": "El dinero sirve para pagar lo que compramos."},
    {"nivel": 1, "q": "Tienes 2 monedas de $5. ¿Cuánto dinero tienes?", "op": ["$10", "$7", "$25"], "ok": "$10", "exp": "5 + 5 = 10. Tienes $10."},
    {"nivel": 2, "q": "Tienes $50 y compras algo que cuesta $30. ¿Cuánto queda?", "op": ["$10", "$20", "$30"], "ok": "$20", "exp": "50 - 30 = 20. Quedan $20."},
    {"nivel": 2, "q": "¿Cuál puede ser una necesidad básica?", "op": ["Videojuego", "Juguete", "Agua"], "ok": "Agua", "exp": "El agua es necesaria para vivir."},
    {"nivel": 2, "q": "Una manzana cuesta $12 y pagas con un billete de $20. ¿Cuánto es tu cambio?", "op": ["$8", "$12", "$10"], "ok": "$8", "exp": "20 - 12 = 8. Tu cambio es de $8."},
    {"nivel": 3, "q": "Un producto cuesta $15. ¿Qué billete puede cubrir el precio?", "op": ["$10", "$5", "$20"], "ok": "$20", "exp": "Con $20 pagas $15 y recibes $5 de cambio."},
    {"nivel": 3, "q": "Quieres ahorrar para una mochila. ¿Qué puede ayudarte?", "op": ["Gastar todo hoy", "Guardar una parte", "No revisar el precio"], "ok": "Guardar una parte", "exp": "Guardar poco a poco ayuda a alcanzar una meta."},
    {"nivel": 3, "q": "Compras un pan de $18 y una leche de $24. ¿Cuánto pagas en total?", "op": ["$32", "$42", "$52"], "ok": "$42", "exp": "18 + 24 = 42. En total pagas $42."},
    {"nivel": 4, "q": "Compras un jabón de $16 y un pan de $18. Pagas con $50. ¿Cuánto es tu cambio?", "op": ["$16", "$34", "$26"], "ok": "$16", "exp": "Primero suma: 16 + 18 = 34. Luego resta: 50 - 34 = 16."},
    {"nivel": 4, "q": "Tu meta de ahorro es $300 y llevas $120. ¿Cuánto te falta?", "op": ["$120", "$180", "$420"], "ok": "$180", "exp": "300 - 120 = 180. Te faltan $180."},
    {"nivel": 4, "q": "Este mes recibiste $200 y gastaste $35. ¿Cuánto es la diferencia?", "op": ["$235", "$165", "$35"], "ok": "$165", "exp": "200 - 35 = 165. La diferencia es de $165."},
    {"nivel": 5, "q": "Tu meta es ahorrar $500 y llevas $125. ¿Qué porcentaje llevas?", "op": ["10%", "25%", "50%"], "ok": "25%", "exp": "125 es la cuarta parte de 500, es decir, el 25%."},
    {"nivel": 5, "q": "¿Cuál de estas opciones es un deseo, no una necesidad?", "op": ["Comida del día", "Medicina", "Un videojuego nuevo"], "ok": "Un videojuego nuevo", "exp": "Un deseo es algo que te gustaría tener, pero puede esperar."},
    {"nivel": 5, "q": "Tienes $100. Compras un cuaderno de $35 y unos colores de $42. ¿Te alcanza para un jabón de $16?", "op": ["Sí, y me quedan $7", "No, me faltan $7", "Sí, y me quedan $23"], "ok": "Sí, y me quedan $7", "exp": "35 + 42 = 77. Te quedan 100 - 77 = 23. Con 23 pagas el jabón de 16 y sobran $7."},
    {"nivel": 5, "q": "Ahorras $25 cada semana. ¿En cuántas semanas llegas a $100?", "op": ["3 semanas", "4 semanas", "5 semanas"], "ok": "4 semanas", "exp": "25 por 4 semanas es 100. Son 4 semanas."},
]


def responder(opcion):
    i = st.session_state.reto_i
    st.session_state.reto_intentos += 1
    n = st.session_state.reto_intentos
    if opcion == RETOS[i]["ok"]:
        st.session_state.reto_estrellas[i] = 3 if n == 1 else 2 if n == 2 else 1
        st.session_state.reto_puntos += (10 if n == 1 else 5 if n == 2 else 2) * RETOS[i]["nivel"]
        st.session_state.reto_feedback = "ok"
    else:
        st.session_state.reto_feedback = "fail"


def siguiente_reto():
    st.session_state.reto_i += 1
    st.session_state.reto_intentos = 0
    st.session_state.reto_feedback = None


def reto_map(i_actual, estrellas):
    n = len(RETOS)
    xs, ys = [150, 380, 620, 850], [585, 445, 305, 175]
    pos = [(xs[k % 4] if (k // 4) % 2 == 0 else xs[3 - (k % 4)], ys[k // 4]) for k in range(n)]
    crown = (150, 60)

    def seg(a, b):
        (x1, y1), (x2, y2) = a, b
        if y1 == y2 or x1 == x2:
            return f"M{x1} {y1} L{x2} {y2}"
        bulge = 110 if x1 > 500 else -110
        return f"M{x1} {y1} C{x1 + bulge} {y1 - 10} {x2 + bulge} {y2 + 10} {x2} {y2}"

    rnd = random.Random(7)
    colors = ["#FF4D8D", "#7C4DFF", "#00B894", "#FFB300", "#29B6F6", "#FF7043"]
    sprinkles = "".join(
        f'<rect x="{rnd.randint(30, 970)}" y="{rnd.randint(30, 630)}" width="14" height="6" rx="3" '
        f'fill="{rnd.choice(colors)}" opacity=".55"/>'
        for _ in range(45)
    )
    deco = [
        ("🍭", 55, 545, 54), ("🍬", 500, 520, 46), ("🍩", 260, 380, 50), ("🍬", 740, 380, 46),
        ("🍭", 940, 380, 54), ("🧁", 500, 245, 50), ("🍪", 250, 245, 44), ("🍓", 750, 245, 44),
        ("🍒", 640, 75, 48), ("🍩", 780, 85, 48), ("🏰", 930, 100, 60), ("🍭", 60, 330, 50),
    ]
    deco_svg = "".join(f'<text x="{x}" y="{y}" font-size="{s}" text-anchor="middle" opacity=".9">{e}</text>' for e, x, y, s in deco)
    paths = ""
    for k in range(n):
        d = seg(pos[k], pos[k + 1] if k + 1 < n else crown)
        stripe = "#2ECC71" if k < i_actual else "#F48FB1"
        paths += (
            f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="30" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{stripe}" stroke-width="30" stroke-dasharray="16 16"/>'
        )
    nodes = ""
    for k, (x, y) in enumerate(pos):
        lvl = RETOS[k]["nivel"]
        color = NIVELES[lvl][2]
        if k < i_actual:
            got = estrellas.get(k, 0)
            stars = "".join(
                f'<text x="{x + dx}" y="{y + 72}" font-size="28" text-anchor="middle" '
                f'fill="{"#FFC107" if idx < got else "#E0E0E0"}">★</text>'
                for idx, dx in enumerate((-26, 0, 26))
            )
            nodes += (
                f'<g><circle cx="{x}" cy="{y}" r="42" fill="{color}" stroke="#FFD54F" stroke-width="8"/>'
                f'<text x="{x}" y="{y}" dy=".35em" font-size="34" font-weight="800" text-anchor="middle" fill="#fff">{k + 1}</text>'
                f'<text x="{x}" y="{y - 48}" font-size="30" text-anchor="middle">👑</text>{stars}</g>'
            )
        elif k == i_actual:
            nodes += (
                f'<g><circle cx="{x}" cy="{y}" r="46" fill="{color}" stroke="#FFFFFF" stroke-width="9"/>'
                f'<text x="{x}" y="{y}" dy=".35em" font-size="40" font-weight="800" text-anchor="middle" fill="#fff">{k + 1}</text>'
                f'<text x="{x}" y="{y - 58}" font-size="44" text-anchor="middle">🦄</text></g>'
            )
        else:
            nodes += (
                f'<g><circle cx="{x}" cy="{y}" r="40" fill="#B0BEC5" stroke="#FFFFFF" stroke-width="7"/>'
                f'<text x="{x}" y="{y}" dy=".35em" font-size="32" font-weight="800" text-anchor="middle" fill="#ECEFF1">{k + 1}</text>'
                f'<text x="{x}" y="{y + 66}" font-size="22" text-anchor="middle">🔒</text></g>'
            )
    html = (
        "<style>body{margin:0;background:transparent}svg{width:100%;height:auto;display:block;max-width:1100px;margin:0 auto}</style>"
        '<svg viewBox="0 0 1000 660" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="5" y="5" width="990" height="650" rx="26" fill="#FFF59D" stroke="#D81B60" stroke-width="10"/>'
        f"{sprinkles}{deco_svg}{paths}"
        '<text x="150" y="75" font-size="76" text-anchor="middle">👑</text>'
        '<text x="330" y="90" font-size="58" font-weight="900" fill="#E53935">¡LA META!</text>'
        f"{nodes}</svg>"
    )
    components.html(html, height=740)


def reiniciar_retos():
    st.session_state.reto_i = 0
    st.session_state.reto_intentos = 0
    st.session_state.reto_feedback = None
    st.session_state.reto_estrellas = {}
    st.session_state.reto_puntos = 0
    st.session_state.reto_celebrado = False


# ---------------------------------------------------------------
# Banner Principal con Título Grande e Ilustración Inclusiva
# ---------------------------------------------------------------
HERO_ILLUSTRATION_SVG = """
<svg viewBox="0 0 320 155" width="320" height="155" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="4" width="312" height="147" rx="22" fill="rgba(255,255,255,0.22)" stroke="rgba(255,255,255,0.65)" stroke-width="2.5"/>
  <!-- Estrellas y símbolos flotantes -->
  <text x="24" y="34" font-size="20" font-weight="900" fill="#FFF59D">★</text>
  <text x="148" y="28" font-size="18" font-weight="900" fill="#FFFFFF">1 2 3</text>
  <text x="275" y="34" font-size="20" font-weight="900" fill="#FFF59D">★</text>
  <text x="22" y="138" font-size="18" font-weight="900" fill="#FFF59D">A B C</text>
  <text x="262" y="138" font-size="18" font-weight="900" fill="#FFF59D">$10</text>

  <!-- Moneda grande brillante -->
  <circle cx="92" cy="40" r="15" fill="#FFD54F" stroke="#FFF" stroke-width="2.5"/>
  <text x="92" y="45" font-size="15" font-weight="900" fill="#E65100" text-anchor="middle">$</text>
  <circle cx="228" cy="40" r="15" fill="#FFD54F" stroke="#FFF" stroke-width="2.5"/>
  <text x="228" y="45" font-size="15" font-weight="900" fill="#E65100" text-anchor="middle">$</text>

  <!-- Personaje 1: Niño alegre -->
  <g transform="translate(36, 52)">
    <circle cx="32" cy="24" r="16" fill="#FFCC80"/>
    <path d="M16 20 Q32 4 48 20" fill="#4E342E"/>
    <circle cx="27" cy="23" r="2.2" fill="#263238"/>
    <circle cx="37" cy="23" r="2.2" fill="#263238"/>
    <path d="M27 30 Q32 35 37 30" stroke="#263238" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <rect x="15" y="42" width="34" height="36" rx="12" fill="#29B6F6" stroke="#FFF" stroke-width="2"/>
  </g>

  <!-- Personaje 2: Joven con lentes (centro) -->
  <g transform="translate(118, 42)">
    <circle cx="42" cy="28" r="20" fill="#3E2723"/>
    <circle cx="42" cy="30" r="18" fill="#F5CBA7"/>
    <circle cx="35" cy="29" r="5.5" stroke="#7C4DFF" stroke-width="2.3" fill="none"/>
    <circle cx="49" cy="29" r="5.5" stroke="#7C4DFF" stroke-width="2.3" fill="none"/>
    <line x1="40.5" y1="29" x2="43.5" y2="29" stroke="#7C4DFF" stroke-width="2.2"/>
    <path d="M35 37 Q42 43 49 37" stroke="#263238" stroke-width="2.4" fill="none" stroke-linecap="round"/>
    <rect x="20" y="50" width="44" height="44" rx="15" fill="#FF4D8D" stroke="#FFF" stroke-width="2.2"/>
    <text x="42" y="77" font-size="16" font-weight="900" fill="#FFF" text-anchor="middle">🌈</text>
  </g>

  <!-- Personaje 3: Adulto / Adulto mayor -->
  <g transform="translate(214, 48)">
    <circle cx="34" cy="26" r="18" fill="#ECEFF1"/>
    <circle cx="34" cy="28" r="16" fill="#8D5524"/>
    <circle cx="28" cy="27" r="2.2" fill="#FFF"/>
    <circle cx="40" cy="27" r="2.2" fill="#FFF"/>
    <path d="M28 34 Q34 39 40 34" stroke="#FFF" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <rect x="15" y="46" width="38" height="40" rx="14" fill="#00B894" stroke="#FFF" stroke-width="2"/>
  </g>
</svg>
"""

saludo_personal = f"¡Hola, {st.session_state.nombre.strip()}! " if st.session_state.nombre.strip() else ""
st.markdown(
    f'<div class="kikipay-hero">'
    f'<div class="kikipay-hero-text">'
    f'<div class="kikipay-title">🌈 KikiPay Inclusivo</div>'
    f"<h3>{saludo_personal}Aprender sobre el dinero, paso a paso y a tu propio ritmo.</h3>"
    f"<p>Toca cualquier icono grande para entrar directo a esa actividad. No hay prisa.</p>"
    f"</div>"
    f'<div class="kikipay-hero-art">{HERO_ILLUSTRATION_SVG}</div>'
    f"</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Menú superior de iconos grandes
# ---------------------------------------------------------------
for fila in (SECCIONES[:4], SECCIONES[4:]):
    nav_cols = st.columns(4)
    for col_idx, (sec_full, icon, short_label) in enumerate(fila):
        with nav_cols[col_idx]:
            es_actual = st.session_state.seccion_actual == sec_full
            etiqueta = f"{icon}\n{short_label} ✓" if es_actual else f"{icon}\n{short_label}"
            st.button(etiqueta, key=f"nav_top_{sec_full}", use_container_width=True, on_click=ir_a, args=(sec_full,))

st.divider()
section = st.session_state.seccion_actual

if section == "🏠 Inicio":
    header("¡Bienvenido/a!")
    st.write("Toca cualquier icono de arriba para abrir una actividad. Puedes volver aquí cuando quieras.")
    inc, exp, balance = totals()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Saldo de práctica", money(balance))
    c2.metric("🌱 Ahorro registrado", money(st.session_state.ahorro_actual))
    c3.metric("🎯 Meta de ahorro", money(st.session_state.meta_ahorro))
    st.write("")
    msg("success", "Puedes repetir las actividades todas las veces que quieras. No hay prisa.")

elif section == "🪙 Conozco el dinero":
    header("🪙 Conozco el dinero")
    hint("Observa la tarjeta, elige la cantidad y presiona Comprobar.")
    examples = {"Una moneda de $5": 5, "Dos monedas de $10": 20, "Un billete de $20": 20, "Un billete de $50": 50, "Cinco monedas de $10": 50}
    prompt("Observa esta representación:")
    item = st.selectbox("Representación", list(examples.keys()), label_visibility="collapsed")
    subheader("💵 " + item)
    prompt("¿Cuánto dinero representa?")
    answer = st.radio("Cantidad", [5, 10, 20, 30, 50, 100], horizontal=True, key="money_answer", label_visibility="collapsed")
    if st.button("Comprobar cantidad", key="check_money"):
        if answer == examples[item]:
            msg("success", "¡Correcto! Identificaste la cantidad. 🎉")
        else:
            msg("warning", "Vuelve a mirar la representación e inténtalo otra vez.")
    st.divider()
    subheader("➕ Practica una suma")
    a, b = st.columns(2)
    with a:
        first = st.selectbox("Primera cantidad", [1, 2, 5, 10, 20], key="sum_first")
    with b:
        second = st.selectbox("Segunda cantidad", [1, 2, 5, 10, 20], key="sum_second")
    prompt(f"¿Cuánto es {first} más {second}?")
    result = st.number_input("Escribe el total", min_value=0, max_value=100, step=1, key="sum_result")
    if st.button("Revisar suma", key="check_sum"):
        if result == first + second:
            msg("success", f"¡Muy bien! {first} + {second} = {first + second}.")
        else:
            msg("info", f"Pista: empieza con {first} y agrega {second}.")

elif section == "🛍️ Practico compras":
    header("🛍️ Practico compras")
    hint("Selecciona un producto, revisa el precio y elige cuánto dinero entregas.")
    products = {"🍎 Manzana": 12, "🥛 Leche": 24, "🍞 Pan": 18, "📒 Cuaderno": 35, "🖍️ Colores": 42, "🧼 Jabón": 16}
    prompt("¿Qué quieres comprar?")
    product = st.selectbox("Producto", list(products.keys()), label_visibility="collapsed")
    price = products[product]
    st.metric("Precio", money(price))
    prompt("¿Cuánto dinero entregas?")
    paid = st.selectbox("Dinero entregado", [10, 20, 50, 100, 200], index=2, label_visibility="collapsed")
    if st.button("Calcular cambio", key="calculate_change"):
        if paid < price:
            msg("error", f"Te faltan {money(price - paid)}.")
        else:
            msg("success", f"Tu cambio sería {money(paid - price)}. ¡Buen trabajo!")
    st.caption("Simulación educativa: no realiza compras ni pagos reales.")

elif section == "📊 Organizo mi dinero":
    header("📊 Organizo mi dinero")
    hint("Completa los campos y presiona Guardar movimiento. Puedes usar datos ficticios.")
    with st.form("movement_form", clear_on_submit=True):
        kind = st.radio("Tipo de movimiento", ["Ingreso", "Gasto"], horizontal=True)
        concept = st.text_input("Concepto", placeholder="Ej. dinero para transporte")
        amount = st.number_input("Cantidad en pesos", min_value=0.0, step=1.0)
        category = st.selectbox("Categoría", ["Alimentación", "Transporte", "Educación", "Hogar", "Diversión", "Salud", "Ahorro", "Otro"])
        submitted = st.form_submit_button("Guardar movimiento")
    if submitted:
        if amount <= 0:
            msg("error", "Escribe una cantidad mayor que cero.")
        else:
            add_movement(kind, concept.strip(), category, amount)
            msg("success", "¡Movimiento guardado en esta sesión!")
    inc, exp, balance = totals()
    a, b, c = st.columns(3)
    a.metric("Ingresos", money(inc))
    b.metric("Gastos", money(exp))
    c.metric("Diferencia", money(balance))
    if st.session_state.movimientos:
        subheader("Mis movimientos")
        st.dataframe(pd.DataFrame(st.session_state.movimientos), use_container_width=True, hide_index=True)
        if st.button("Borrar todos los movimientos", key="clear_movements"):
            st.session_state.movimientos = []
            st.rerun()
    else:
        msg("info", "Todavía no hay movimientos. Agrega uno de práctica para comenzar.")

elif section == "🌱 Mi ahorro":
    header("🌱 Mi ahorro")
    hint("Define una meta y registra cuánto llevas ahorrado.")
    prompt("Mi meta de ahorro (pesos)")
    goal = st.number_input("Meta", min_value=1.0, value=float(st.session_state.meta_ahorro), step=10.0, label_visibility="collapsed")
    prompt("¿Cuánto llevo ahorrado? (pesos)")
    saved = st.number_input("Ahorrado", min_value=0.0, value=float(st.session_state.ahorro_actual), step=5.0, label_visibility="collapsed")
    st.session_state.meta_ahorro = goal
    st.session_state.ahorro_actual = saved
    progress = min(saved / goal, 1.0)
    st.progress(progress)
    msg("info", f"Avance: **{progress * 100:.0f}%**")
    remaining = max(goal - saved, 0)
    if remaining == 0:
        msg("success", "¡Meta alcanzada! ¡Felicidades! 🎉")
    else:
        msg("info", f"Te faltan {money(remaining)} para llegar a tu meta.")

elif section == "🎮 Retos y juegos":
    header("🎮 Retos y juegos")
    hint("Lee la pregunta y elige una respuesta. Puedes intentarlo las veces que quieras.")
    total = len(RETOS)
    i = st.session_state.reto_i
    estrellas = sum(st.session_state.reto_estrellas.values())
    nivel_actual = RETOS[min(i, total - 1)]["nivel"]
    st.markdown(
        f'<div class="score-row">'
        f'<div class="score" style="background:#FF6B9D">⭐ Estrellas<br><span style="font-size:1.4em">{estrellas} / {total * 3}</span></div>'
        f'<div class="score" style="background:#7C4DFF">🏅 Puntos<br><span style="font-size:1.4em">{st.session_state.reto_puntos}</span></div>'
        f'<div class="score" style="background:#00B894">🎯 Reto<br><span style="font-size:1.4em">{min(i + 1, total)} de {total}</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )
    reto_map(i, st.session_state.reto_estrellas)
    chips = ""
    for lvl, (icon, name, color, _bg) in NIVELES.items():
        idxs = [k for k, r in enumerate(RETOS) if r["nivel"] == lvl]
        done = all(k < i for k in idxs)
        current = (lvl == nivel_actual and i < total)
        style, mark = (f"background:{color}", "✅") if done else ((f"background:{color};outline:5px solid #FFD600", "👉") if current else ("background:#B0BEC5", "🔒"))
        chips += f'<div class="chip" style="{style}">{mark} {icon} Nivel {lvl}<br>{name}</div>'
    st.markdown(f'<div class="path">{chips}</div>', unsafe_allow_html=True)
    st.progress(min(i / total, 1.0))
    if i >= total:
        if not st.session_state.reto_celebrado:
            st.balloons()
            st.session_state.reto_celebrado = True
        msg("success", f"🏆 ¡Terminaste todos los retos! Lograste {estrellas} de {total * 3} estrellas y {st.session_state.reto_puntos} puntos. ¡Felicidades!")
        st.button("🔄 Jugar otra vez", key="reto_reiniciar", on_click=reiniciar_retos)
    else:
        reto = RETOS[i]
        icon, name, color, bg = NIVELES[reto["nivel"]]
        q_html = reto["q"].replace("$", "&#36;")
        st.markdown(
            f'<div class="reto-card" style="background:{bg};border-color:{color};color:#263238">'
            f'<div style="font-weight:700;color:{color};margin-bottom:.3rem">{icon} Nivel {reto["nivel"]} · {name}</div>'
            f'<div style="font-size:1.15em;font-weight:600;color:#263238">{q_html}</div></div>',
            unsafe_allow_html=True,
        )
        listo = st.session_state.reto_feedback == "ok"
        cols = st.columns(len(reto["op"]))
        for j, opt in enumerate(reto["op"]):
            with cols[j]:
                st.button(opt.replace("$", "\\$"), key=f"reto_{i}_{j}", use_container_width=True, disabled=listo, on_click=responder, args=(opt,))
        fb = st.session_state.reto_feedback
        if fb == "ok":
            n = st.session_state.reto_estrellas[i]
            msg("success", f"¡Respuesta correcta! 🌟 {reto['exp']} Ganaste {'⭐' * n}")
            st.button("Ver mis resultados 🏆" if i == total - 1 else "Siguiente reto ➡️", key="reto_siguiente", on_click=siguiente_reto, use_container_width=True)
        elif fb == "fail":
            msg("warning", "Casi. Puedes volver a intentarlo. Pista: " + reto["exp"])

elif section == "💬 Ayuda KikiPay":
    header("💬 Ayuda KikiPay")
    st.write("Escribe una pregunta. Esta versión usa explicaciones educativas preparadas; no necesita una API.")
    question = st.text_input("¿Qué quieres aprender?", placeholder="Ej. ¿Qué significa ahorrar?")
    if st.button("Ver explicación", key="ask_kikipay"):
        q = question.lower().strip()
        answers = [
            (["ahorrar", "ahorro"], "Ahorrar significa guardar una parte del dinero para utilizarla después. Puedes elegir una meta y avanzar poco a poco."),
            (["cambio", "vuelto"], "El cambio es el dinero que recibes cuando entregas más de lo que cuesta un producto. Resta: dinero entregado menos precio."),
            (["presupuesto", "organizar"], "Un presupuesto es un plan para organizar el dinero que recibes y decidir cómo utilizarlo."),
            (["necesidad", "deseo"], "Una necesidad es algo importante para vivir o estar bien, como alimentos o agua. Un deseo es algo que te gustaría tener, pero puede esperar."),
            (["precio", "comparar"], "Para comparar precios, observa cuánto cuesta cada opción y qué cantidad o características ofrece."),
        ]
        reply = next((text for words, text in answers if any(word in q for word in words)), None)
        if reply:
            msg("success", reply)
        elif q:
            msg("info", "Puedo explicar: ahorro, cambio, presupuesto, necesidades, deseos y comparación de precios.")
        else:
            msg("warning", "Escribe una pregunta o una palabra sobre el tema.")
    st.caption("Este asistente básico no es un chatbot generativo y no envía preguntas a internet.")

elif section == "⚙️ Mi experiencia":
    header("⚙️ Mi experiencia")
    st.write("Adapta la aplicación a tus preferencias.")
    st.session_state.nombre = st.text_input("Nombre o apodo (opcional)", value=st.session_state.nombre)
    st.session_state.tamano_letra = st.select_slider("Tamaño de letra", options=["Pequeña", "Mediana", "Grande", "Muy grande"], value=st.session_state.tamano_letra)
    st.session_state.alto_contraste = st.toggle("Activar alto contraste", value=st.session_state.alto_contraste)
    st.session_state.mostrar_pistas = st.toggle("Mostrar instrucciones paso a paso", value=st.session_state.mostrar_pistas)
    st.divider()
    subheader("Datos de demostración")
    demo_choice = st.toggle("Cargar ejemplo de demostración", value=st.session_state.modo_demo)
    if demo_choice and not st.session_state.modo_demo:
        st.session_state.movimientos = [
            {"Fecha": str(date.today()), "Tipo": "Ingreso", "Concepto": "Dinero de práctica", "Categoría": "Otro", "Cantidad": 200.0},
            {"Fecha": str(date.today()), "Tipo": "Gasto", "Concepto": "Cuaderno", "Categoría": "Educación", "Cantidad": 35.0},
        ]
        st.session_state.ahorro_actual = 120.0
        st.session_state.meta_ahorro = 300.0
        st.session_state.modo_demo = True
        st.rerun()
    elif not demo_choice and st.session_state.modo_demo:
        st.session_state.movimientos = []
        st.session_state.ahorro_actual = 0.0
        st.session_state.meta_ahorro = 500.0
        st.session_state.modo_demo = False
        st.rerun()
    msg("success", "Tus preferencias se aplican durante esta sesión.")

st.divider()
st.caption("KikiPay Inclusivo · Herramienta educativa. No ofrece asesoría financiera, no realiza pagos y no diagnostica. Utiliza datos ficticios o de práctica.")
