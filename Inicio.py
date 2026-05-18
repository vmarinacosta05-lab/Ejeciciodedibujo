import streamlit as st
import base64
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas
import random

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Fábulas Mágicas ✨",
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
st.title("📖✨ Fábulas Mágicas para Niños")
st.subheader("Dibuja un personaje y crea una historia increíble 🌈")

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.header("🪄 Personaliza la historia")

    moraleja = st.selectbox(
        "💡 Elige una moraleja",
        [
            "La amistad es importante",
            "Nunca rendirse",
            "Ser amable con los demás",
            "Decir siempre la verdad",
            "Trabajar en equipo",
            "Compartir con otros"
        ]
    )

    lugar = st.selectbox(
        "🌍 Lugar de la aventura",
        [
            "Bosque mágico",
            "Castillo encantado",
            "Espacio",
            "Selva misteriosa",
            "Océano brillante",
            "Pueblo fantástico"
        ]
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
# FRASES ALEATORIAS
# =========================
frases = [
    "🌟 Tu imaginación puede crear mundos mágicos",
    "🦄 Cada dibujo tiene una historia escondida",
    "📚 Los mejores personajes nacen aquí",
    "✨ Hoy puedes inventar algo increíble"
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
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=350,
    width=500,
    drawing_mode="freedraw",
    key="canvas",
)

# =========================
# BOTÓN CREAR HISTORIA
# =========================
if st.button("✨ Crear Fábula"):

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
            Analiza este dibujo infantil.

            Describe:
            - Qué personaje parece ser
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
        # CREAR HISTORIA
        # =========================
        with st.spinner("📖 Creando fábula mágica..."):

            historia_prompt = f"""
            Basado en esta descripción:

            {descripcion}

            Crea una fábula infantil corta y divertida.

            La historia debe:
            - Ocurrir en: {lugar}
            - Tener diálogos simples
            - Ser muy imaginativa
            - Tener un final feliz
            - Enseñar esta moraleja:
              '{moraleja}'

            Usa lenguaje fácil para niños.
            """

            historia_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": historia_prompt
                    }
                ],
                max_tokens=700,
            )

            historia = historia_response.choices[0].message.content

            st.session_state.historia = historia

            st.markdown("## 🌟 Tu Fábula Mágica")

            st.markdown(
                f"""
                <div class="story-box">
                {historia}
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
