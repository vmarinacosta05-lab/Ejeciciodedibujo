import streamlit as st
from openai import OpenAI
import random

# =========================
# CONFIGURACIÓN DE LA APP
# =========================
st.set_page_config(
    page_title="Creador de Fábulas ✨",
    page_icon="📖",
    layout="centered"
)

# =========================
# ESTILOS PERSONALIZADOS
# =========================
st.markdown("""
<style>
.main {
    background: linear-gradient(to bottom, #fff8e7, #ffe4ec);
}

h1 {
    text-align: center;
    color: #ff4b91;
    font-size: 3rem;
}

h2, h3 {
    color: #6a4c93;
}

.stButton>button {
    background-color: #ff4b91;
    color: white;
    border-radius: 15px;
    border: none;
    padding: 10px 20px;
    font-size: 18px;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #ff85b3;
    transform: scale(1.05);
}

.story-box {
    background-color: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    margin-top: 20px;
}

.footer {
    text-align: center;
    margin-top: 40px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.title("📖✨ Creador de Fábulas para Niños")
st.subheader("Crea historias mágicas con moralejas increíbles 🌈")

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("🪄 Personaliza tu historia")

    protagonista = st.text_input(
        "👦 Nombre del protagonista",
        placeholder="Ej: Sofía"
    )

    animal = st.selectbox(
        "🐶 Elige un animal",
        [
            "León", "Conejo", "Tortuga", "Zorro",
            "Elefante", "Perro", "Gato", "Búho"
        ]
    )

    lugar = st.selectbox(
        "🌳 Lugar de la historia",
        [
            "Bosque mágico",
            "Castillo encantado",
            "Selva",
            "Espacio",
            "Océano",
            "Pueblo mágico"
        ]
    )

    enseñanza = st.selectbox(
        "💡 Moraleja",
        [
            "La amistad es importante",
            "Nunca rendirse",
            "Ser amable con los demás",
            "Decir siempre la verdad",
            "Trabajar en equipo"
        ]
    )

# =========================
# API KEY
# =========================
api_key = st.text_input(
    "🔑 Ingresa tu API Key de OpenAI",
    type="password"
)

# =========================
# FRASES BONITAS
# =========================
frases = [
    "🌟 Cada historia es una aventura nueva",
    "🦄 La imaginación no tiene límites",
    "📚 Las mejores historias nacen aquí",
    "✨ Hoy puedes crear magia"
]

st.info(random.choice(frases))

# =========================
# BOTÓN PRINCIPAL
# =========================
if st.button("✨ Crear Fábula"):

    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API Key.")
    else:

        client = OpenAI(api_key=api_key)

        with st.spinner("📖 Creando una historia mágica..."):

            prompt = f"""
            Crea una fábula infantil corta y divertida en español.

            Personaje principal: {protagonista}
            Animal: {animal}
            Lugar: {lugar}

            La historia debe:
            - Ser tierna y divertida
            - Fácil de entender para niños
            - Tener diálogos simples
            - Incluir una moraleja sobre:
            '{enseñanza}'
            - Tener un final feliz
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
            )

            historia = response.choices[0].message.content

            st.markdown("## 🌟 Tu Fábula")

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
✨ Hecho con Streamlit + OpenAI ✨
</div>
""", unsafe_allow_html=True)
