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

.main {
    background: linear-gradient(to bottom, #fff7d6, #ffe8f3);
}

h1 {
    text-align: center;
    color: #ff4b91;
    font-size: 3.2rem;
}

h2, h3 {
    color: #6a4c93;
}

.stButton>button {
    background-color: #ff4b91;
    color: white;
    border-radius: 15px;
    border: none;
    padding: 12px 22px;
    font-size: 18px;
    transition: 0.3s;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #ff85b3;
    transform: scale(1.05);
}

.story-box {
    background-color: white;
    padding: 25px;
    border-radius: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    margin-top: 20px;
    font-size: 18px;
    line-height: 1.7;
}

.tip-box {
    background-color: #fff0f7;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    color: #6a4c93;
    font-weight: bold;
}

.footer {
    text-align: center;
    margin-top: 40px;
    color: gray;
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
st.title("📖✨ Cuentos de Macondo")
st.subheader("Dibuja un personaje y crea un cuento con realismo mágico 🦋")

# =========================
# SIDEBAR  (CAMBIADO: ahora pincel, grosor y género)
# =========================
with st.sidebar:

    st.header("🪄 Personaliza tu cuento")

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
st.markdown("## 🎨 Dibuja tu personaje")

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

            st.markdown("### 🧸 Tu personaje")
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
            historia_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", historia)
            historia_html = historia_html.replace("\n", "<br>")

            st.markdown("## 🌟 Tu Cuento")

            st.markdown(
                f"""
                <div class="story-box">
                {historia_html}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.balloons()

# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
✨ Hecho por Valentina Marin y Samuel Acevedo✨
</div>
""", unsafe_allow_html=True)
