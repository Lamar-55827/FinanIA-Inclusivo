import re
import json
import random
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

# ---------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------
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
    "mostrar_voz": True,
    "modo_demo": False,
    # Retos
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
# Apariencia accesible y colorida (sin barra lateral)
# ---------------------------------------------------------------
font_sizes = {"Pequeña": 16, "Mediana": 18, "Grande": 21, "Muy grande": 24}
font_px = font_sizes[st.session_state.tamano_letra]
HC = st.session_state.alto_contraste

if HC:
    app_bg = "#101820"
    fg, card, border = "#FFFFFF", "#202D38", "#FFFFFF"
    btn_bg, btn_fg = "#FFD600", "#000000"
else:
    app_bg = (
        "linear-gradient(135deg,#FFE3F1 0%,#E4EEFF 30%,"
        "#DDFBF0 60%,#FFF3C9 100%)"
    )
    fg, card, border = "#263238", "#FFFFFF", "#CBB8FF"
    btn_bg, btn_fg = "linear-gradient(135deg,#7C4DFF,#00B8A9)", "#FFFFFF"

st.markdown(f"""
<style>
/* Ocultar barra lateral */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{
  display: none !important;
}}
.stApp {{ background: {app_bg}; background-attachment: fixed; color: {fg}; }}
html, body, [class*="st-"], p, label, li {{ font-size: {font_px}px; }}
.block-container {{ max-width: 1180px; padding-top: 1.2rem; padding-bottom: 3rem; }}
.kikipay-hero {{
  background: linear-gradient(120deg,#FF4D8D,#FF8A00,#00B894,#6C5CE7);
  color:#FFFFFF; padding:1.25rem 1.5rem; border-radius:22px; margin-bottom:.8rem;
  text-shadow: 0 2px 4px rgba(0,0,0,.35); box-shadow: 0 6px 18px rgba(108,92,231,.35);
}}
.kikipay-hero h1, .kikipay-hero h3, .kikipay-hero p {{ color:#FFFFFF; margin:.2rem 0; }}
[data-testid="stMetric"] {{
  background:{card}; border:2px solid {border};
  border-left: 10px solid #FF6B9D; border-radius:16px; padding:.8rem 1rem;
  box-shadow: 0 3px 10px rgba(0,0,0,.08);
}}
div.stButton > button, div.stFormSubmitButton > button {{
  min-height: 3.4rem;
  border-radius: 18px;
  font-weight: 800;
  border: none;
  background: {btn_bg};
  color: {btn_fg};
  box-shadow: 0 4px 10px rgba(0,0,0,.18);
  transition: transform .15s, filter .15s;
  padding: 0.55rem 0.8rem;
  white-space: pre-line !important;
  line-height: 1.25 !important;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
  transform: scale(1.03); filter: brightness(1.08);
}}
div.stButton > button p {{
  color: {btn_fg};
  font-size: {font_px + 1}px !important;
  white-space: pre-line !important;
  overflow: visible !important;
  text-overflow: unset !important;
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
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Voz directa en cada botón (sin setTimeout ni bloqueo cross-origin)
# con respaldo automático si el navegador no tiene voces locales.
# ---------------------------------------------------------------
SPEAK_JS = """
(function(){
  const synth = window.speechSynthesis;
  let audioFallback = null;

  function norm(v){ return (v.lang || '').replace('_', '-').toLowerCase(); }

  function pickVoice(){
    if (!synth) return null;
    const vs = synth.getVoices();
    const prefer = ['dalia','sabina','paulina','monica','helena','google','mujer','female'];
    const byName = list => {
      for (const n of prefer){
        const f = list.find(v => v.name.toLowerCase().includes(n));
        if (f) return f;
      }
      return list[0];
    };
    let l = vs.filter(v => norm(v) === 'es-mx'); if (l.length) return byName(l);
    l = vs.filter(v => norm(v) === 'es-us');     if (l.length) return byName(l);
    l = vs.filter(v => norm(v).startsWith('es'));if (l.length) return byName(l);
    return null;
  }

  if (synth){
    synth.getVoices();
    synth.onvoiceschanged = function(){ synth.getVoices(); };
  }

  function stopAll(btn){
    if (synth){
      try { synth.cancel(); } catch(e){}
    }
    if (audioFallback){
      try { audioFallback.pause(); audioFallback.currentTime = 0; } catch(e){}
      audioFallback = null;
    }
    document.querySelectorAll('.b.on').forEach(b => b.classList.remove('on'));
  }

  function playFallbackTTS(text, btn){
    const chunks = text.match(/.{1,180}(\\s|$)/g) || [text];
    let idx = 0;
    btn.classList.add('on');
    function next(){
      if (idx >= chunks.length){
        btn.classList.remove('on');
        return;
      }
      const q = encodeURIComponent(chunks[idx].trim());
      idx++;
      audioFallback = new Audio('https://translate.googleapis.com/translate_tts?ie=UTF-8&client=tw-ob&tl=es-MX&q=' + q);
      audioFallback.onended = next;
      audioFallback.onerror = function(){ btn.classList.remove('on'); };
      audioFallback.play().catch(function(){ btn.classList.remove('on'); });
    }
    next();
  }

  window.hablar = function(text, btn){
    const yaActivo = btn.classList.contains('on');
    stopAll(btn);
    if (yaActivo) return;

    if (synth){
      try {
        if (synth.paused) synth.resume();
        const u = new SpeechSynthesisUtterance(text);
        const v = pickVoice();
        if (v){ u.voice = v; u.lang = v.lang; } else { u.lang = 'es-MX'; }
        u.rate = 0.92;
        u.pitch = 1.05;
        u.volume = 1;
        window.__kikiUtterance = u;

        let inicioConfirmado = false;
        u.onstart = function(){ inicioConfirmado = true; };
        u.onend = function(){ btn.classList.remove('on'); window.__kikiUtterance = null; };
        u.onerror = function(){
          window.__kikiUtterance = null;
          playFallbackTTS(text, btn);
        };

        btn.classList.add('on');
        synth.speak(u);

        // Si en 450ms el navegador no arrancó la voz local, activar respaldo de audio
        setTimeout(function(){
          if (!inicioConfirmado && !synth.speaking){
            try { synth.cancel(); } catch(e){}
            playFallbackTTS(text, btn);
          }
        }, 450);
        return;
      } catch(e){}
    }
    playFallbackTTS(text, btn);
  };
})();
"""

BTN_CSS = """
body{margin:0;background:transparent;font-family:'Segoe UI',Arial,sans-serif;}
.b{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:none;cursor:pointer;
   color:#fff;background:linear-gradient(135deg,#FF4D8D,#7C4DFF);border-radius:999px;
   min-height:46px;min-width:46px;padding:0 15px;font-size:22px;
   box-shadow:0 3px 8px rgba(0,0,0,.25);transition:transform .15s;}
.b:hover{transform:scale(1.06);}
.b span{font-size:16px;font-weight:700;}
.b.on{background:linear-gradient(135deg,#00B894,#00C9FF);animation:pulso 1s infinite;}
@keyframes pulso{0%{box-shadow:0 0 0 0 rgba(0,184,148,.7);}100%{box-shadow:0 0 0 14px rgba(0,184,148,0);}}
"""


def clean_for_speech(text):
    """Convierte texto con formato a algo que suene natural al leerlo."""
    t = str(text)

    def _money(m):
        num = m.group(1).replace(",", "")
        if num.endswith(".00"):
            num = num[:-3]
        return f"{num} pesos"

    t = re.sub(r"\$\s?([\d,]+(?:\.\d+)?)(\s?MXN)?", _money, t)
    t = re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u200d]", "", t)
    t = t.replace("**", "").replace("*", "").replace("`", "")
    t = t.replace("%", " por ciento").replace(" + ", " más ")
    t = t.replace(" - ", " menos ").replace(" = ", " es igual a ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def speak_button(text, label=None):
    """Botón de altavoz. Al tocarlo lee el texto en español."""
    if not st.session_state.mostrar_voz:
        return
    speech = json.dumps(clean_for_speech(text), ensure_ascii=False).replace("</", "<\\/")
    inner = f"🔊<span>{label}</span>" if label else "🔊"
    html = (
        f"<style>{BTN_CSS}</style>"
        f'<button class="b" aria-label="Escuchar" title="Escuchar" '
        f'onclick="hablar({speech}, this)">{inner}</button>'
        f"<script>{SPEAK_JS}</script>"
    )
    components.html(html, height=56)


def md_safe(text):
    return str(text).replace("$", "\\$")


def header(text, speech=None):
    if st.session_state.mostrar_voz:
        c1, c2 = st.columns([1, 10], vertical_alignment="center")
        with c1:
            speak_button(speech or text)
        with c2:
            st.header(md_safe(text))
    else:
        st.header(md_safe(text))


def subheader(text, speech=None):
    if st.session_state.mostrar_voz:
        c1, c2 = st.columns([1, 10], vertical_alignment="center")
        with c1:
            speak_button(speech or text)
        with c2:
            st.subheader(md_safe(text))
    else:
        st.subheader(md_safe(text))


def msg(kind, text, speech=None):
    if st.session_state.mostrar_voz:
        c1, c2 = st.columns([1, 10], vertical_alignment="center")
        with c1:
            speak_button(speech or text)
        with c2:
            getattr(st, kind)(md_safe(text))
    else:
        getattr(st, kind)(md_safe(text))


def prompt(text, speech=None):
    if st.session_state.mostrar_voz:
        c1, c2 = st.columns([1, 10], vertical_alignment="center")
        with c1:
            speak_button(speech or text)
        with c2:
            st.markdown("**" + md_safe(text) + "**")
    else:
        st.markdown("**" + md_safe(text) + "**")


def hint(message):
    if st.session_state.mostrar_pistas:
        msg("info", "**Paso a paso:** " + message, "Paso a paso. " + message)


def interactive_module_card(icon, title, desc, accent, bg, target_section, btn_key):
    """Tarjeta visual con bocina independiente Y botón funcional de Streamlit para abrir el módulo."""
    if HC:
        bg, text_color = "#202D38", "#FFFFFF"
        accent = "#FFD600"
    else:
        text_color = "#263238"

    speech = json.dumps(clean_for_speech(f"{title}. {desc}"), ensure_ascii=False)
    html = f"""
<style>
{BTN_CSS}
.c{{
  background:{bg}; border:4px solid {accent}; border-radius:20px 20px 8px 8px;
  padding:14px 16px; height:165px; box-sizing:border-box; position:relative;
  box-shadow:0 4px 12px rgba(0,0,0,.10);
}}
.ic{{font-size:46px;line-height:1;}}
h4{{margin:8px 0 4px;color:{text_color};font-size:{font_px + 2}px;}}
p{{margin:0;color:{text_color};font-size:{font_px - 1}px;}}
.sp{{position:absolute;top:10px;right:10px;}}
</style>
<div class="c">
  <div class="sp"><button class="b" aria-label="Escuchar" onclick='hablar({speech}, this)'>🔊</button></div>
  <div class="ic">{icon}</div>
  <h4>{title}</h4>
  <p>{desc}</p>
</div>
<script>{SPEAK_JS}</script>
"""
    components.html(html, height=175)
    st.button(
        f"Abrir {icon} {title}",
        key=btn_key,
        use_container_width=True,
        on_click=ir_a,
        args=(target_section,),
    )


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


# ---------------------------------------------------------------
# Retos: de muy fáciles a difíciles
# ---------------------------------------------------------------
NIVELES = {
    1: ("🌱", "Muy fácil", "#43A047", "#E3F6E4"),
    2: ("🌿", "Fácil", "#00ACC1", "#DDF5F9"),
    3: ("🌳", "Medio", "#FB8C00", "#FFEFD9"),
    4: ("🌟", "Difícil", "#E53935", "#FFE3E2"),
    5: ("🏆", "Experto", "#8E24AA", "#F3E1F8"),
}

RETOS = [
    {"nivel": 1, "q": "¿Cuánto vale una moneda de $10?",
     "op": ["$5", "$10", "$20"], "ok": "$10",
     "exp": "La moneda dice 10, así que vale $10."},
    {"nivel": 1, "q": "¿Cuál de estas cosas sirve para pagar?",
     "op": ["Una nube", "Dinero", "Un lápiz"], "ok": "Dinero",
     "exp": "El dinero sirve para pagar lo que compramos."},
    {"nivel": 1, "q": "Tienes 2 monedas de $5. ¿Cuánto dinero tienes?",
     "op": ["$10", "$7", "$25"], "ok": "$10",
     "exp": "5 + 5 = 10. Tienes $10."},
    {"nivel": 2, "q": "Tienes $50 y compras algo que cuesta $30. ¿Cuánto queda?",
     "op": ["$10", "$20", "$30"], "ok": "$20",
     "exp": "50 - 30 = 20. Quedan $20."},
    {"nivel": 2, "q": "¿Cuál puede ser una necesidad básica?",
     "op": ["Videojuego", "Juguete", "Agua"], "ok": "Agua",
     "exp": "El agua es necesaria para vivir."},
    {"nivel": 2, "q": "Una manzana cuesta $12 y pagas con un billete de $20. ¿Cuánto es tu cambio?",
     "op": ["$8", "$12", "$10"], "ok": "$8",
     "exp": "20 - 12 = 8. Tu cambio es de $8."},
    {"nivel": 3, "q": "Un producto cuesta $15. ¿Qué billete puede cubrir el precio?",
     "op": ["$10", "$5", "$20"], "ok": "$20",
     "exp": "Con $20 pagas $15 y recibes $5 de cambio."},
    {"nivel": 3, "q": "Quieres ahorrar para una mochila. ¿Qué puede ayudarte?",
     "op": ["Gastar todo hoy", "Guardar una parte", "No revisar el precio"],
     "ok": "Guardar una parte",
     "exp": "Guardar poco a poco ayuda a alcanzar una meta."},
    {"nivel": 3, "q": "Compras un pan de $18 y una leche de $24. ¿Cuánto pagas en total?",
     "op": ["$32", "$42", "$52"], "ok": "$42",
     "exp": "18 + 24 = 42. En total pagas $42."},
    {"nivel": 4, "q": "Compras un jabón de $16 y un pan de $18. Pagas con $50. ¿Cuánto es tu cambio?",
     "op": ["$16", "$34", "$26"], "ok": "$16",
     "exp": "Primero suma: 16 + 18 = 34. Luego resta: 50 - 34 = 16."},
    {"nivel": 4, "q": "Tu meta de ahorro es $300 y llevas $120. ¿Cuánto te falta?",
     "op": ["$120", "$180", "$420"], "ok": "$180",
     "exp": "300 - 120 = 180. Te faltan $180."},
    {"nivel": 4, "q": "Este mes recibiste $200 y gastaste $35. ¿Cuánto es la diferencia?",
     "op": ["$235", "$165", "$35"], "ok": "$165",
     "exp": "200 - 35 = 165. La diferencia es de $165."},
    {"nivel": 5, "q": "Tu meta es ahorrar $500 y llevas $125. ¿Qué porcentaje llevas?",
     "op": ["10%", "25%", "50%"], "ok": "25%",
     "exp": "125 es la cuarta parte de 500, es decir, el 25%."},
    {"nivel": 5, "q": "¿Cuál de estas opciones es un deseo, no una necesidad?",
     "op": ["Comida del día", "Medicina", "Un videojuego nuevo"], "ok": "Un videojuego nuevo",
     "exp": "Un deseo es algo que te gustaría tener, pero puede esperar."},
    {"nivel": 5, "q": "Tienes $100. Compras un cuaderno de $35 y unos colores de $42. ¿Te alcanza para un jabón de $16?",
     "op": ["Sí, y me quedan $7", "No, me faltan $7", "Sí, y me quedan $23"],
     "ok": "Sí, y me quedan $7",
     "exp": "35 + 42 = 77. Te quedan 100 - 77 = 23. Con 23 pagas el jabón de 16 y sobran $7."},
    {"nivel": 5, "q": "Ahorras $25 cada semana. ¿En cuántas semanas llegas a $100?",
     "op": ["3 semanas", "4 semanas", "5 semanas"], "ok": "4 semanas",
     "exp": "25 por 4 semanas es 100. Son 4 semanas."},
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
    xs = [150, 380, 620, 850]
    ys = [585, 445, 305, 175]
    pos = []
    for k in range(n):
        row, col = divmod(k, 4)
        x = xs[col] if row % 2 == 0 else xs[3 - col]
        pos.append((x, ys[row]))
    crown = (150, 60)

    def seg(a, b):
        (x1, y1), (x2, y2) = a, b
        if y1 == y2 or x1 == x2:
            return f"M{x1} {y1} L{x2} {y2}"
        bulge = 110 if x1 > 500 else -110
        return f"M{x1} {y1} C{x1 + bulge} {y1 - 10} {x2 + bulge} {y2 + 10} {x2} {y2}"

    rnd = random.Random(7)
    sprinkles = ""
    colors = ["#FF4D8D", "#7C4DFF", "#00B894", "#FFB300", "#29B6F6", "#FF7043"]
    for _ in range(45):
        sx, sy = rnd.randint(30, 970), rnd.randint(30, 630)
        sprinkles += (f'<rect x="{sx}" y="{sy}" width="14" height="6" rx="3" fill="{rnd.choice(colors)}" '
                      f'opacity=".55" transform="rotate({rnd.randint(0, 180)} {sx} {sy})"/>')

    deco = [("🍭", 55, 545, 54), ("🍬", 500, 520, 46), ("🍩", 260, 380, 50), ("🍬", 740, 380, 46),
            ("🍭", 940, 380, 54), ("🧁", 500, 245, 50), ("🍪", 250, 245, 44), ("🍓", 750, 245, 44),
            ("🍒", 640, 75, 48), ("🍩", 780, 85, 48), ("🏰", 930, 100, 60), ("🍭", 60, 330, 50)]
    deco_svg = "".join(f'<text x="{x}" y="{y}" font-size="{s}" text-anchor="middle" opacity=".9">{e}</text>'
                       for e, x, y, s in deco)

    paths = ""
    for k in range(n):
        a = pos[k]
        b = pos[k + 1] if k + 1 < n else crown
        d = seg(a, b)
        hecho = k < i_actual
        stripe = "#2ECC71" if hecho else "#F48FB1"
        paths += (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="30" stroke-linecap="round"/>'
                  f'<path d="{d}" fill="none" stroke="{stripe}" stroke-width="30" stroke-dasharray="16 16"/>')

    nodes = ""
    for k, (x, y) in enumerate(pos):
        lvl = RETOS[k]["nivel"]
        color = NIVELES[lvl][2]
        nombre = NIVELES[lvl][1]
        if k < i_actual:
            got = estrellas.get(k, 0)
            stars = "".join(
                f'<text x="{x + dx}" y="{y + 72}" font-size="28" text-anchor="middle" '
                f'fill="{"#FFC107" if idx < got else "#E0E0E0"}" stroke="#fff" stroke-width="1">★</text>'
                for idx, dx in enumerate((-26, 0, 26)))
            nodes += (f'<g><title>Reto {k + 1}: {nombre}</title>'
                      f'<circle cx="{x}" cy="{y}" r="42" fill="{color}" stroke="#FFD54F" stroke-width="8"/>'
                      f'<text x="{x}" y="{y}" dy=".35em" font-size="34" font-weight="800" text-anchor="middle" '
                      f'fill="#fff" stroke="rgba(0,0,0,.35)" stroke-width="4" paint-order="stroke">{k + 1}</text>'
                      f'<text x="{x}" y="{y - 48}" font-size="30" text-anchor="middle">👑</text>{stars}</g>')
        elif k == i_actual:
            nodes += (f'<g><title>Reto {k + 1}: estás aquí</title>'
                      f'<circle cx="{x}" cy="{y}" r="46" fill="none" stroke="#FFD600" stroke-width="6">'
                      f'<animate attributeName="r" values="46;66;46" dur="1.4s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values="1;0;1" dur="1.4s" repeatCount="indefinite"/></circle>'
                      f'<circle cx="{x}" cy="{y}" r="46" fill="{color}" stroke="#FFFFFF" stroke-width="9"/>'
                      f'<text x="{x}" y="{y}" dy=".35em" font-size="40" font-weight="800" text-anchor="middle" '
                      f'fill="#fff" stroke="rgba(0,0,0,.35)" stroke-width="4" paint-order="stroke">{k + 1}</text>'
                      f'<g><animateTransform attributeName="transform" type="translate" '
                      f'values="0 0;0 -12;0 0" dur="0.9s" repeatCount="indefinite"/>'
                      f'<text x="{x}" y="{y - 58}" font-size="44" text-anchor="middle">🦄</text></g></g>')
        else:
            nodes += (f'<g><title>Reto {k + 1}: todavía bloqueado</title>'
                      f'<circle cx="{x}" cy="{y}" r="40" fill="#B0BEC5" stroke="#FFFFFF" stroke-width="7"/>'
                      f'<text x="{x}" y="{y}" dy=".35em" font-size="32" font-weight="800" text-anchor="middle" '
                      f'fill="#ECEFF1" stroke="rgba(0,0,0,.25)" stroke-width="3" paint-order="stroke">{k + 1}</text>'
                      f'<text x="{x}" y="{y + 66}" font-size="22" text-anchor="middle">🔒</text></g>')

    fin = i_actual >= n
    glow = ('<circle cx="150" cy="55" r="58" fill="#FFF176" opacity=".8">'
            '<animate attributeName="r" values="50;70;50" dur="1.2s" repeatCount="indefinite"/></circle>') if fin else ""
    html = f"""
<style>body{{margin:0;background:transparent}}
svg{{width:100%;height:auto;display:block;max-width:1100px;margin:0 auto;
font-family:'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji','Segoe UI',Arial,sans-serif}}</style>
<svg viewBox="0 0 1000 660" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mapa de retos">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#FFF59D"/><stop offset=".3" stop-color="#C8F2A5"/>
<stop offset=".65" stop-color="#FFC4E3"/><stop offset="1" stop-color="#D5C2FF"/></linearGradient></defs>
<rect x="5" y="5" width="990" height="650" rx="26" fill="url(#bg)" stroke="#D81B60" stroke-width="10"/>
{sprinkles}{deco_svg}{paths}
{glow}<text x="150" y="75" font-size="76" text-anchor="middle">👑</text>
<text x="330" y="90" font-size="58" font-weight="900" font-style="italic" fill="#E53935" stroke="#FFFFFF"
stroke-width="8" paint-order="stroke" text-anchor
