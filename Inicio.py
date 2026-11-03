import streamlit as st
import base64
import re
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas
import random

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Cuentos de Macondo ✨",
    page_icon="📖",
    layout="centered"
)

# =========================
# SESSION STATE
# =========================
if "historia" not in st.session_state:
    st.session_state.historia = ""

if "descripcion_personaje" not in st.session_state:
    st.session_state.descripcion_personaje = ""

# =========================
# ESTILOS
# =========================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

/* ---------- Fondo tipo papel antiguo ---------- */
.stApp {
    background:
        radial-gradient(ellipse at top, #fbf3dc 0%, #f1e4c3 60%, #e6d4a8 100%);
    color: #3b2a1a;
    font-family: 'EB Garamond', Georgia, serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2.5rem;
    max-width: 780px;
}

/* ---------- Texto general ---------- */
.stApp p, .stApp li, .stApp label {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 1.15rem;
    color: #3b2a1a;
}

/* ---------- Títulos ---------- */
.kicker {
    text-align: center;
    font-family: 'EB Garamond', Georgia, serif;
    font-variant: small-caps;
    letter-spacing: 4px;
    font-size: 1.05rem;
    color: #8b6b3d;
    margin-bottom: -10px;
}

.stApp h1, [data-testid="stHeading"] h1 {
    font-family: 'Playfair Display', Georgia, serif !important;
    text-align: center;
    color: #3b2a1a !important;
    font-size: 3.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px;
    line-height: 1.15 !important;
    padding: 0.4rem 0 0.2rem 0 !important;
}

.stApp h1::after, [data-testid="stHeading"] h1::after {
    content: "";
    display: block;
    width: 180px;
    height: 2px;
    margin: 16px auto 4px auto;
    background: linear-gradient(to right, transparent, #a47a2c, transparent);
}

h2, h3 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #5a3a1c !important;
    font-weight: 500 !important;
}

[data-testid="stHeading"] h3,
.stApp h3 {
    font-style: italic;
}

/* Subtítulo centrado y en cursiva */
.stApp h3:first-of-type {
    text-align: center;
    font-size: 1.35rem !important;
    font-weight: 400 !important;
    color: #6b4a22 !important;
}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #e9d8ad, #dcc791);
    border-right: 2px solid #b79a5b;
}

[data-testid="stSidebar"] h2 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #4a2e14 !important;
    border-bottom: 1px solid #a47a2c;
    padding-bottom: 0.4rem;
}

[data-testid="stSidebar"] label p {
    font-weight: 500;
    font-size: 1.05rem !important;
    color: #4a2e14 !important;
}

[data-testid="stSidebar"] input[type="color"] {
    border-radius: 50%;
    border: 2px solid #a47a2c;
}

/* ---------- Iconos (restaurar fuente) ---------- */
[data-testid="stIconMaterial"],
.material-icons,
[class*="material-symbols"] {
    font-family: "Material Symbols Rounded", "Material Icons" !important;
}

/* ---------- Flecha para abrir / cerrar la barra lateral ---------- */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] button,
[data-testid="collapsedControl"] button {
    background: #fbf3dc !important;
    color: #5a3a1c !important;
    border: 1px solid #a47a2c !important;
    border-radius: 50% !important;
    width: 38px;
    height: 38px;
    box-shadow: 0px 3px 8px rgba(60, 30, 10, 0.25);
    transition: 0.25s;
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stExpandSidebarButton"] button:hover,
[data-testid="collapsedControl"] button:hover {
    background: #7a2e2e !important;
    color: #fbf3dc !important;
    border-color: #3b1212 !important;
    transform: scale(1.1);
}

[data-testid="stSidebarCollapseButton"] button *,
[data-testid="stExpandSidebarButton"] *,
[data-testid="collapsedControl"] button * {
    color: inherit !important;
}

/* ---------- Campos de texto y selectores ---------- */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: #fbf3dc !important;
    border: 1px solid #b79a5b !important;
    border-radius: 6px !important;
}

/* ---------- Botón ---------- */
.stButton>button {
    background: linear-gradient(to bottom, #7a2e2e, #5c1f1f);
    color: #fbf3dc;
    border-radius: 6px;
    border: 1px solid #3b1212;
    padding: 12px 28px;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 18px;
    letter-spacing: 1px;
    transition: 0.3s;
    box-shadow: 0px 3px 8px rgba(60, 30, 10, 0.35);
}

.stButton>button p {
    color: #fbf3dc !important;
}

.stButton>button:hover {
    background: linear-gradient(to bottom, #944040, #6e2626);
    border-color: #3b1212;
    transform: translateY(-2px);
}

/* ---------- Cita / epígrafe ---------- */
.tip-box {
    text-align: center;
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 1.15rem;
    color: #6b4a22;
    padding: 14px 20px;
    margin: 10px 0 25px 0;
    border-top: 1px solid #b79a5b;
    border-bottom: 1px solid #b79a5b;
}

/* ---------- Marco del lienzo de dibujo ---------- */
iframe {
    border: 3px double #8b6b3d !important;
    border-radius: 4px;
    box-shadow: 0px 6px 18px rgba(60, 30, 10, 0.25);
}

/* ---------- Página del cuento ---------- */
.story-box {
    position: relative;
    background:
        linear-gradient(to right, rgba(120,90,40,0.12), transparent 6%),
        #fdf8e8;
    padding: 50px 60px 45px 60px;
    margin: 30px 0;
    border: 1px solid #c9b27a;
    border-radius: 3px;
    box-shadow:
        0px 12px 30px rgba(60, 30, 10, 0.30),
        inset 0 0 40px rgba(180, 140, 70, 0.18);
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 1.28rem;
    line-height: 1.85;
    color: #2e2014;
}

.story-box .story-title {
    font-family: 'Playfair Display', Georgia, serif;
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: #3b2a1a;
    margin: 0 0 6px 0;
    line-height: 1.25;
}

.story-box .ornament {
    width: 160px;
    height: 2px;
    margin: 4px auto 28px auto;
    background: linear-gradient(to right, transparent, #a47a2c, transparent);
}

.story-box p {
    text-align: justify;
    text-indent: 1.6em;
    margin: 0 0 6px 0;
    font-size: 1.28rem;
    color: #2e2014;
}

.story-box p:first-of-type {
    text-indent: 0;
}

.story-box p:first-of-type::first-letter {
    font-family: 'Playfair Display', Georgia, serif;
    float: left;
    font-size: 4.2rem;
    line-height: 0.85;
    padding: 6px 10px 0 0;
    color: #7a2e2e;
    font-weight: 700;
}

.story-box .end-mark {
    text-align: center;
    color: #a47a2c;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.6rem;
    letter-spacing: 8px;
    margin-top: 25px;
}

/* ---------- Footer ---------- */
.footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 15px;
    border-top: 1px solid #b79a5b;
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    color: #7a6038;
}

@media (max-width: 640px) {
    .story-box { padding: 30px 24px; }
    h1 { font-size: 2.2rem !important; }
}

</style>
""", unsafe_allow_html=True)

# =========================
# FUNCIÓN BASE64
# =========================
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# =========================
# TÍTULO
# =========================
st.markdown('<div class="kicker">Homenaje a Gabriel García Márquez</div>', unsafe_allow_html=True)
st.title("Cuentos de Macondo")
st.subheader("Dibuja un personaje y deja que la historia nazca de tu trazo")

# =========================
# SIDEBAR  (CAMBIADO: ahora pincel, grosor y género)
# =========================
with st.sidebar:

    st.header("✒️ Personaliza tu cuento")

    genero = st.selectbox(
        "🎭 Elige el género del cuento",
        [
            "Realismo mágico",
            "Romance",
            "Misterio",
            "Nostalgia y recuerdos",
            "Aventura",
            "Drama familiar",
            "Fantasía"
        ]
    )

    personaje_gabo = st.selectbox(
        "👤 Personajes de Gabo",
        [
            "Ninguno",
            "Remedios la Bella (Cien años de soledad)",
            "Úrsula Iguarán (Cien años de soledad)",
            "Coronel Aureliano Buendía (Cien años de soledad)",
            "Melquíades (Cien años de soledad)",
            "Pilar Ternera (Cien años de soledad)",
            "Florentino Ariza (El amor en los tiempos del cólera)",
            "Fermina Daza (El amor en los tiempos del cólera)",
            "Santiago Nasar (Crónica de una muerte anunciada)",
            "Eréndira y su abuela (La increíble y triste historia de la cándida Eréndira)",
            "El coronel (El coronel no tiene quien le escriba)",
            "El hombre muy viejo con unas alas enormes (Un señor muy viejo con unas alas enormes)"
        ]
    )

    stroke_color = st.color_picker(
        "🎨 Color del pincel",
        "#000000"
    )

    stroke_width = st.slider(
        "🖍️ Grosor del pincel",
        1,
        25,
        5
    )

# =========================
# API KEY
# =========================
api_key = st.text_input(
    "🔑 Ingresa tu API Key de OpenAI",
    type="password"
)

# =========================
# FRASES ALEATORIAS  (CAMBIADO: frases en tono literario)
# =========================
frases = [
    "🌟 Tu imaginación puede crear mundos mágicos",
    "🦋 Cada dibujo guarda un cuento esperando ser contado",
    "📚 Los mejores personajes nacen aquí",
    "☔ Quizás hoy llueva durante cuatro años en tu historia"
]

st.markdown(
    f"""
    <div class="tip-box">
    {random.choice(frases)}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# CANVAS DE DIBUJO
# =========================
st.markdown("## ✎ Dibuja tu personaje")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=350,
    width=500,
    drawing_mode="freedraw",
    key="canvas",
)

# =========================
# BOTÓN CREAR HISTORIA
# =========================
if st.button("✨ Crear Cuento"):

    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API Key.")

    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja un personaje primero.")

    else:

        client = OpenAI(api_key=api_key)

        with st.spinner("🎨 Analizando dibujo..."):

            # Convertir dibujo
            img_array = np.array(canvas_result.image_data)

            image = Image.fromarray(
                img_array.astype("uint8")
            ).convert("RGBA")

            image.save("personaje.png")

            base64_image = encode_image("personaje.png")

            # =========================
            # ANALIZAR DIBUJO
            # =========================
            descripcion_prompt = """
            Analiza este dibujo.

            Describe:
            - Qué personaje, objeto o figura parece ser
            - Cómo se ve
            - Qué emociones transmite

            Responde en español de forma corta y amigable.
            """

            descripcion_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": descripcion_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
            )

            descripcion = descripcion_response.choices[0].message.content

            st.session_state.descripcion_personaje = descripcion

            st.success("🎉 ¡Personaje descubierto!")

            st.markdown("### Tu personaje")
            st.write(descripcion)

        # =========================
        # CREAR HISTORIA  (CAMBIADO: prompt con la esencia de Gabo)
        # =========================
        with st.spinner("📖 Escribiendo tu cuento..."):

            estilo_gabo = """
            Eres un escritor que domina el estilo literario de Gabriel García Márquez
            y del realismo mágico latinoamericano. Tu escritura tiene estas características:
            - Lo extraordinario se cuenta con total naturalidad, como si fuera cotidiano.
            - Narrador omnisciente, sereno, casi de abuelo que cuenta una historia antigua.
            - Frases largas, musicales y llenas de imágenes sensoriales
              (olores, calor, lluvia, colores, flores, mariposas).
            - Juegos con el tiempo: saltos al pasado y al futuro, y la sensación de que
              el tiempo es circular.
            - Temas de soledad, memoria, nostalgia, amor y destino.
            - Un pueblo caribeño o colombiano como escenario, con aire de leyenda.
            - Detalles exagerados y poéticos (hipérboles) presentados como hechos reales.
            - Un final que cierre con una imagen poética o un giro inesperado.
            Escribes siempre en español. No copias textos ni frases de sus obras:
            creas una historia totalmente original inspirada en su estilo.
            """

            if personaje_gabo == "Ninguno":
                instruccion_personaje = ""
            else:
                instruccion_personaje = (
                    f"- Hacer que lo dibujado y el personaje {personaje_gabo} "
                    "sean protagonistas juntos: se encuentran e interactúan en una "
                    "situación nueva y original, respetando la personalidad y la "
                    "esencia del personaje, sin copiar escenas ni frases de la obra"
                )

            historia_prompt = f"""
            Basado en esta descripción de un dibujo:

            {descripcion}

            Escribe un cuento corto de UNA sola página (entre 300 y 400 palabras).

            El cuento debe:
            - Tener como protagonista o elemento central lo que aparece en el dibujo
            {instruccion_personaje}
            - Ser del género: {genero}
            - Tener un título original en la primera línea
            - Tener la esencia y el estilo de Gabriel García Márquez
            - Incluir al menos un elemento mágico contado como algo normal
            - Tener un final memorable
            """

            historia_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": estilo_gabo
                    },
                    {
                        "role": "user",
                        "content": historia_prompt
                    }
                ],
                max_tokens=900,
                temperature=0.9,
            )

            historia = historia_response.choices[0].message.content

            st.session_state.historia = historia

            # Dar formato para que se vea bien dentro del recuadro
            # Separar título y párrafos para darle forma de página de libro
            lineas = [l.strip() for l in historia.strip().split("\n") if l.strip()]
            titulo = re.sub(r"^(#+\s*|\*+|T[íi]tulo:\s*)", "", lineas[0])
            titulo = re.sub(r"\*+", "", titulo).strip()
            titulo = re.sub(r"^T[íi]tulo:\s*", "", titulo).strip(' "«»')
            parrafos = [
                re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
                for p in lineas[1:]
            ]
            cuerpo_html = "".join(f"<p>{p}</p>" for p in parrafos)
            historia_html = (
                f'<div class="story-title">{titulo}</div>'
                f'<div class="ornament"></div>'
                f'{cuerpo_html}'
                f'<div class="end-mark">* * *</div>'
            )

            st.markdown("## Tu cuento")

            st.markdown(
                f"""
                <div class="story-box">
                {historia_html}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
✨ Hecho por Valentina Marin y Samuel Acevedo✨
</div>
""", unsafe_allow_html=True)
