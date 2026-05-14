import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Configuración de la app
st.set_page_config(page_title='Detector de Perros 🐶')
st.title('🐶 Detector de Razas de Perros')
st.subheader("Dibuja un perro y descubre qué raza podría ser")

# Sidebar
with st.sidebar:
    st.subheader("Acerca de")
    st.write("Esta app analiza un dibujo e intenta identificar la raza del perro y dar información útil.")

# Canvas
stroke_width = st.sidebar.slider('Grosor del trazo', 1, 30, 5)

canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# API Key
api_key = st.text_input('Ingresa tu API Key', type="password")

# ✅ Cliente creado con la key del input
client = OpenAI(api_key=api_key)

# Botón de análisis
if st.button("🔍 Analizar dibujo"):

    if canvas_result.image_data is not None and api_key:

        with st.spinner("Analizando imagen..."):
            # Convertir imagen
            img_array = np.array(canvas_result.image_data)
            image = Image.fromarray(img_array.astype('uint8')).convert('RGBA')
            image.save("perro.png")

            base64_image = encode_image_to_base64("perro.png")

            prompt = (
                "Analiza este dibujo y describe en español qué tipo de perro es. "
                "Si parece una raza conocida, menciona cuál podría ser."
            )

            # ✅ Usar client en lugar de openai directamente
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            resultado = response.choices[0].message.content
            st.session_state.full_response = resultado
            st.session_state.analysis_done = True

            st.markdown("### 🐾 Resultado del análisis")
            st.write(resultado)

    else:
        st.warning("Dibuja algo y agrega tu API Key.")

# Generar información
if st.session_state.analysis_done:

    st.divider()
    st.subheader("📚 Más sobre este perro")

    if st.button("📖 Generar información"):

        with st.spinner("Generando información..."):

            info_prompt = f"""
            Basado en esta descripción: '{st.session_state.full_response}',
            da información breve sobre el perro incluyendo:
            - Características
            - Personalidad
            - Cuidados básicos
            """

            # ✅ Usar client
            info_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": info_prompt}],
                max_tokens=400,
            )

            st.markdown("### 🐶 Información del perro")
            st.write(info_response.choices[0].message.content)

    if st.button("✨ Crear historia"):

        with st.spinner("Creando historia..."):

            historia_prompt = f"""
            Basado en esta descripción: '{st.session_state.full_response}',
            crea una historia infantil corta y divertida sobre este perro.
            """

            # ✅ Usar client
            historia_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": historia_prompt}],
                max_tokens=400,
            )

            st.markdown("### 📖 Historia")
            st.write(historia_response.choices[0].message.content)
            st.write(story_response.choices[0].message.content)

# Warnings for user action required
if not api_key:
    st.warning("Por favor ingresa tu API key.")
