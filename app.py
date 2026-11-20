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
stroke-width="8" paint-order="stroke" text-anchor="start">¡LA META!</text>
{nodes}
</svg>
"""
    components.html(html, height=740)


def reiniciar_retos():
    st.session_state.reto_i = 0
    st.session_state.reto_intentos = 0
    st.session_state.reto_feedback = None
    st.session_state.reto_estrellas = {}
    st.session_state.reto_puntos = 0
    st.session_state.reto_celebrado = False


# ---------------------------------------------------------------
# Encabezado principal
# ---------------------------------------------------------------
saludo_personal = (
    f"¡Hola, {st.session_state.nombre.strip()}! "
    if st.session_state.nombre.strip()
    else ""
)
st.markdown(f"""
<div class="kikipay-hero">
<h1>🌈 KikiPay Inclusivo</h1>
<h3>{saludo_personal}Aprender sobre el dinero, paso a paso y a tu propio ritmo.</h3>
<p>Toca cualquier icono grande para entrar directo a esa actividad. No hay prisa.</p>
</div>
""", unsafe_allow_html=True)

speak_button(
    f"{saludo_personal}Bienvenido a KikiPay Inclusivo. Aprende sobre el dinero, paso a paso y a tu propio ritmo. "
    "Toca cualquier icono para entrar directo a esa actividad.",
    label="Escuchar bienvenida",
)

# ---------------------------------------------------------------
# Barra superior de navegación en 2 filas de 4 botones grandes
# para que ningún nombre ni icono se corte con "..."
# ---------------------------------------------------------------
for fila in (SECCIONES[:4], SECCIONES[4:]):
    nav_cols = st.columns(4)
    for col_idx, (sec_full, icon, short_label) in enumerate(fila):
        with nav_cols[col_idx]:
            es_actual = st.session_state.seccion_actual == sec_full
            etiqueta = f"{icon}\n{short_label} ✓" if es_actual else f"{icon}\n{short_label}"
            st.button(
                etiqueta,
                key=f"nav_top_{sec_full}",
                use_container_width=True,
                on_click=ir_a,
                args=(sec_full,),
            )

st.divider()

section = st.session_state.seccion_actual

# ---------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------
if section == "🏠 Inicio":
    header("¡Bienvenido/a!", "Bienvenido. Toca la tarjeta o el icono de la actividad que quieras hacer.")
    st.write("Toca cualquier tarjeta para comenzar. Puedes volver al inicio cuando quieras.")

    inc, exp, balance = totals()
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Saldo de práctica", money(balance))
    c2.metric("🌱 Ahorro registrado", money(st.session_state.ahorro_actual))
    c3.metric("🎯 Meta de ahorro", money(st.session_state.meta_ahorro))

    speak_button(
        f"Tu saldo de práctica es {money(balance)}. Tu ahorro registrado es {money(st.session_state.ahorro_actual)}. "
        f"Tu meta de ahorro es {money(st.session_state.meta_ahorro)}.",
        label="Escuchar mis datos",
    )

    subheader("Toca un icono para abrir la actividad")
    cards = [
        ("🪙", "Conocer el dinero", "Reconocer cantidades y practicar sumas.", "#FF6B9D", "#FFE3EE", "🪙 Conozco el dinero"),
        ("🛍️", "Practicar compras", "Elegir productos y calcular el cambio.", "#FF9800", "#FFEFD6", "🛍️ Practico compras"),
        ("📊", "Organizar mi dinero", "Registrar ingresos y gastos.", "#00B894", "#DDF8EF", "📊 Organizo mi dinero"),
        ("🌱", "Mi ahorro", "Crear una meta y observar el progreso.", "#43A047", "#E3F6E4", "🌱 Mi ahorro"),
        ("🎮", "Retos y juegos", "Resolver situaciones cotidianas, de fácil a difícil.", "#7C4DFF", "#EAE3FF", "🎮 Retos y juegos"),
        ("💬", "Ayuda KikiPay", "Consultar explicaciones sencillas.", "#00ACC1", "#DDF5F9", "💬 Ayuda KikiPay"),
    ]
    cols = st.columns(3)
    for idx, (icon, title, desc, accent, bg, target) in enumerate(cards):
        with cols[idx % 3]:
            interactive_module_card(icon, title, desc, accent, bg, target, f"card_open_{idx}")

    st.write("")
    msg("success", "Puedes repetir las actividades todas las veces que quieras.")

elif section == "🪙 Conozco el dinero":
    header("🪙 Conozco el dinero")
    hint("Observa la tarjeta, elige la cantidad y presiona Comprobar.")
    examples = {
        "Una moneda de $5": 5,
        "Dos monedas de $10": 20,
        "Un billete de $20": 20,
        "Un billete de $50": 50,
        "Cinco monedas de $10": 50,
    }
    prompt("Observa esta representación:")
    item = st.selectbox("Representación", list(examples.keys()), label_visibility="collapsed")
    subheader("💵 " + item, item)
    prompt("¿Cuánto dinero representa?")
    answer = st.radio(
        "Cantidad", [5, 10, 20, 30, 50, 100], horizontal=True,
        key="money_answer", label_visibility="collapsed"
    )
    if st.button("Comprobar cantidad", key="check_money"):
        if answer == examples[item]:
            msg("success", "¡Correcto! Identificaste la cantidad. 🎉")
        else:
            msg("warning", "Vuelve a mirar la representación e inténtalo otra vez.")
    st.divider()
    subheader("➕ Practica una suma", "Practica una suma. Elige dos cantidades y escribe el total.")
    a, b = st.columns(2)
    with a:
        first = st.selectbox("Primera cantidad", [1, 2, 5, 10, 20], key="sum_first")
    with b:
        second = st.selectbox("Segunda cantidad", [1, 2, 5, 10, 20], key="sum_second")
    prompt(f"¿Cuánto es {first} más {second}?", f"¿Cuánto es {first} más {second}? Escribe el total.")
    result = st.number_input("Escribe el total", min_value=0, max_value=100, step=1, key="sum_result")
    if st.button("Revisar suma", key="check_sum"):
        if result == first + second:
            msg("success", f"¡Muy bien! {first} + {second} = {first + second}.")
        else:
            msg("info", f"Pista: empieza con {first} y agrega {second}.")

elif section == "🛍️ Practico compras":
    header("🛍️ Practico compras")
    hint("Selecciona un producto, revisa el precio y elige cuánto dinero entregas.")
    products = {
        "🍎 Manzana": 12, "🥛 Leche": 24, "🍞 Pan": 18,
        "📒 Cuaderno": 35, "🖍️ Colores": 42, "🧼 Jabón": 16,
    }
    prompt("¿Qué quieres comprar?")
    product = st.selectbox("Producto", list(products.keys()), label_visibility="collapsed")
    price = products[product]
    st.metric("Precio", money(price))
    speak_button(f"{product} cuesta {money(price)}.", label="Escuchar precio")
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
        category = st.selectbox("Categoría", [
            "Alimentación", "Transporte", "Educación", "Hogar",
            "Diversión", "Salud", "Ahorro", "Otro",
        ])
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
    speak_button(
        f"Tus ingresos son {money(inc)}. Tus gastos son {money(exp)}. "
        f"La diferencia es {money(balance)}.",
        label="Escuchar mis totales",
    )
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
    goal = st.number_input(
        "Meta", min_value=1.0, value=float(st.session_state.meta_ahorro),
        step=10.0, label_visibility="collapsed"
    )
    prompt("¿Cuánto llevo ahorrado? (pesos)")
    saved = st.number_input(
        "Ahorrado", min_value=0.0, value=float(st.session_state.ahorro_actual),
        step=5.0, label_visibility="collapsed"
    )
    st.session_state.meta_ahorro = goal
    st.session_state.ahorro_actual = saved
    progress = min(saved / goal, 1.0)
    st.progress(progress)
    msg("info", f"Avance: **{progress * 100:.0f}%**", f"Llevas un avance de {progress * 100:.0f} por ciento.")
    remaining = max(goal - saved, 0)
    if remaining == 0:
        msg("success", "¡Meta alcanzada! ¡Felicidades! 🎉")
    else:
        msg("info", f"Te faltan {money(remaining)} para llegar a tu meta.")

elif section == "🎮 Retos y juegos":
    header(
        "🎮 Retos y juegos",
        "Retos y juegos. Empiezan muy fáciles y poco a poco suben de nivel. Tómate tu tiempo.",
    )
    hint(
        "Lee la pregunta, toca el altavoz si quieres escucharla y elige una respuesta. "
        "Puedes intentarlo las veces que quieras."
    )

    total = len(RETOS)
    i = st.session_state.reto_i
    estrellas = sum(st.session_state.reto_estrellas.values())
    nivel_actual = RETOS[min(i, total - 1)]["nivel"]

    st.markdown(f"""
<div class="score-row">
  <div class="score" style="background:#FF6B9D">⭐ Estrellas<br><span style="font-size:1.4em">{estrellas} / {total * 3}</span></div>
  <div class="score" style="background:#7C4DFF">🏅 Puntos<br><span style="font-size:1.4em">{st.session_state.reto_puntos}</span></div>
  <div class="score" style="background:#00B894">🎯 Reto<br><span style="font-size:1.4em">{min(i + 1, total)} de {total}</span></div>
</div>
""", unsafe_allow_html=True)

    reto_map(i, st.session_state.reto_estrellas)
    if i < total:
        speak_button(
            f"Vas en el reto {i + 1} de {total}, del nivel {nivel_actual}. "
            f"Llevas {estrellas} estrellas y {st.session_state.reto_puntos} puntos.",
            label="Escuchar dónde voy",
        )
    else:
        speak_button("Llegaste a la meta. ¡Terminaste todos los retos!", label="Escuchar")

    chips = ""
    for lvl, (icon, name, color, _bg) in NIVELES.items():
        idxs = [k for k, r in enumerate(RETOS) if r["nivel"] == lvl]
        done = all(k < i for k in idxs)
        current = (lvl == nivel_actual and i < total)
        if done:
            style, mark = f"background:{color}", "✅"
        elif current:
            style, mark = f"background:{color};outline:5px solid #FFD600", "👉"
        else:
            style, mark = "background:#B0BEC5", "🔒"
        chips += f'<div class="chip" style="{style}">{mark} {icon} Nivel {lvl}<br>{name}</div>'
    st.markdown(f'<div class="path">{chips}</div>', unsafe_allow_html=True)
    st.progress(min(i / total, 1.0))

    if i >= total:
        if not st.session_state.reto_celebrado:
            st.balloons()
            st.session_state.reto_celebrado = True
        msg(
            "success",
            f"🏆 ¡Terminaste todos los retos! Lograste {estrellas} de {total * 3} estrellas "
            f"y {st.session_state.reto_puntos} puntos. ¡Felicidades!",
            f"Terminaste todos los retos. Lograste {estrellas} estrellas de {total * 3} "
            f"y {st.session_state.reto_puntos} puntos. ¡Felicidades!",
        )
        st.write("Puedes volver a jugar para conseguir más estrellas. No hay prisa.")
        st.button("🔄 Jugar otra vez", key="reto_reiniciar", on_click=reiniciar_retos)
    else:
        reto = RETOS[i]
        icon, name, color, bg = NIVELES[reto["nivel"]]
        q_html = reto["q"].replace("$", "&#36;")
        txt = "#263238"
        st.markdown(f"""
<div class="reto-card" style="background:{bg};border-color:{color};color:{txt}">
  <div style="font-weight:700;color:{color};margin-bottom:.3rem">{icon} Nivel {reto['nivel']} · {name}</div>
  <div style="font-size:1.15em;font-weight:600;color:{txt}">{q_html}</div>
</div>
""", unsafe_allow_html=True)
        opciones_voz = ", ".join(reto["op"])
        speak_button(f"{reto['q']} Las opciones son: {opciones_voz}.", label="Escuchar la pregunta")

        listo = st.session_state.reto_feedback == "ok"
        cols = st.columns(len(reto["op"]))
        for j, opt in enumerate(reto["op"]):
            with cols[j]:
                st.button(
                    opt.replace("$", "\\$"), key=f"reto_{i}_{j}", use_container_width=True,
                    disabled=listo, on_click=responder, args=(opt,),
                )

        fb = st.session_state.reto_feedback
        if fb == "ok":
            n = st.session_state.reto_estrellas[i]
            msg(
                "success",
                f"¡Respuesta correcta! 🌟 {reto['exp']} Ganaste {'⭐' * n}",
                f"¡Respuesta correcta! {reto['exp']}",
            )
            st.button(
                "Ver mis resultados 🏆" if i == total - 1 else "Siguiente reto ➡️",
                key="reto_siguiente", on_click=siguiente_reto, use_container_width=True,
            )
        elif fb == "fail":
            msg(
                "warning",
                "Casi. Puedes volver a intentarlo. Pista: " + reto["exp"],
                "Casi. Puedes volver a intentarlo. Pista: " + reto["exp"],
            )

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
    header("⚙️ Mi experiencia", "Mi experiencia. Adapta la aplicación a tus preferencias.")
    st.write("Adapta la aplicación a tus preferencias.")
    st.session_state.nombre = st.text_input("Nombre o apodo (opcional)", value=st.session_state.nombre)
    st.session_state.tamano_letra = st.select_slider(
        "Tamaño de letra", options=["Pequeña", "Mediana", "Grande", "Muy grande"],
        value=st.session_state.tamano_letra,
    )
    st.session_state.alto_contraste = st.toggle("Activar alto contraste", value=st.session_state.alto_contraste)
    st.session_state.mostrar_pistas = st.toggle(
        "Mostrar instrucciones paso a paso", value=st.session_state.mostrar_pistas
    )
    st.session_state.mostrar_voz = st.toggle(
        "Mostrar botones de voz 🔊", value=st.session_state.mostrar_voz
    )

    st.divider()
    subheader("Datos de demostración", "Datos de demostración para practicar con ejemplos.")
    demo_choice = st.toggle("Cargar ejemplo de demostración", value=st.session_state.modo_demo)
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
        st.rerun()
    elif not demo_choice and st.session_state.modo_demo:
        st.session_state.movimientos = []
        st.session_state.ahorro_actual = 0.0
        st.session_state.meta_ahorro = 500.0
        st.session_state.modo_demo = False
        st.rerun()

    speak_button("Hola, soy tu guía de KikiPay. Estoy aquí para acompañarte a tu ritmo.", label="Probar la voz")
    msg("success", "Tus preferencias se aplican durante esta sesión.")
    st.caption("La voz depende del dispositivo: en Edge, Chrome, Android y iPhone suele haber voces en español de México.")

st.divider()
st.caption(
    "KikiPay Inclusivo · Herramienta educativa. No ofrece asesoría financiera, "
    "no realiza pagos y no diagnostica. Utiliza datos ficticios o de práctica."
)
