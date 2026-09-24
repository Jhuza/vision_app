import base64
import hashlib
import streamlit as st
from openai import OpenAI
from aurora import empty_state, footer, hero, section, setup


def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


setup("Visión", "02 / IMÁGENES")
hero("VISIÓN · INTERPRETACIÓN DE IMÁGENES", "Una imagen.", "Más de una lectura.",
     "Explora lo que hay en una imagen. Obtén una descripción en español o añade una pregunta para orientar el análisis.", kind="vision")

left, right = st.columns([1, 1.15], gap="large")
with left:
    with st.container(key="input_panel"):
        section("01", "Tu imagen", "Imagen → contexto")
        api_key = st.text_input("Clave de OpenAI", type="password", placeholder="Ingresa tu clave de API",
                                help="Se utiliza para enviar la imagen y tu pregunta a OpenAI.")
        uploaded_file = st.file_uploader("Carga una imagen", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            with st.expander("Vista previa", expanded=True):
                st.image(uploaded_file, caption=uploaded_file.name, width="stretch")
        show_details = st.toggle("Preguntar algo específico", value=False)
        additional_details = ""
        if show_details:
            additional_details = st.text_area("Tu pregunta o contexto", placeholder="Por ejemplo: ¿qué objetos aparecen y cómo están relacionados?", height=120)
        analyze_button = st.button("Analizar imagen", type="primary", width="stretch")
        st.caption("JPG, JPEG o PNG · Descripción general o pregunta específica.")

image_id = hashlib.sha256(uploaded_file.getvalue()).hexdigest() if uploaded_file else None
credential_id = hashlib.sha256(api_key.encode()).hexdigest() if api_key else None
context_id = (image_id, credential_id, show_details, additional_details)
if st.session_state.get("vision_context") != context_id:
    st.session_state.pop("vision_response", None)
    st.session_state.vision_context = context_id

with right:
    with st.container(key="output_panel"):
        section("02", "Interpretación", "Mirar → comprender")
        if analyze_button:
            if not api_key:
                st.warning("Ingresa tu clave de OpenAI para continuar.")
            elif uploaded_file is None:
                st.warning("Carga una imagen para comenzar el análisis.")
            else:
                st.session_state.pop("vision_response", None)
                prompt_text = "Describe what you see in the image in spanish"
                if show_details and additional_details:
                    prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"
                mime = "image/png" if uploaded_file.name.lower().endswith(".png") else "image/jpeg"
                messages = [{"role": "user", "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encode_image(uploaded_file)}"}},
                ]}]
                message_placeholder = st.empty()
                try:
                    with st.spinner("Interpretando tu imagen…"):
                        full_response = ""
                        with OpenAI(api_key=api_key) as client:
                            for completion in client.chat.completions.create(model="gpt-4o", messages=messages, max_tokens=1200, stream=True):
                                if completion.choices and completion.choices[0].delta.content is not None:
                                    full_response += completion.choices[0].delta.content
                                    message_placeholder.markdown(full_response + "▌")
                        st.session_state.vision_response = full_response
                        message_placeholder.empty()
                except Exception as exc:
                    message_placeholder.empty()
                    st.error(f"No se pudo completar el análisis: {exc}")
        if "vision_response" in st.session_state:
            st.markdown(st.session_state.vision_response)
            st.caption("Interpretación generada por IA. Revisa los detalles importantes en la imagen original.")
        elif not analyze_button:
            empty_state("Otra forma de mirar", "Tu interpretación aparecerá aquí. Puedes pedir una descripción general o centrarte en un detalle.")

footer("IMÁGENES / LENGUAJE / PERSPECTIVA")
