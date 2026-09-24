# Visión · Interfaces multimodales

Interpretación de imágenes con GPT-4o: descripción en español, contexto opcional y respuesta progresiva. Interfaz Aurora con paneles de entrada y resultado, luz azul/naranja y diseño adaptable.

## Ejecutar

Python 3.10 o posterior. Validación local realizada con Python 3.12.

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Introduce tu clave de OpenAI, carga un JPG/JPEG/PNG y pulsa **Analizar imagen**. Activa **Preguntar algo específico** para añadir una pregunta. La imagen y el contexto se envían a OpenAI al pulsar el botón. El cliente se inicia solo tras validar los campos; la clave se muestra como contraseña y no se escribe en variables de entorno compartidas.

Se conservan GPT-4o, el límite de 1200 tokens y la respuesta en streaming. El contenido PNG se identifica con su MIME correcto. El resultado permanece durante la sesión y se descarta cuando cambia la entrada, la clave o el contexto.

## Verificación

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

Pruebas sin llamadas de pago: arranque sin clave, validación, carga de imagen, pregunta opcional, MIME, respuesta progresiva, conservación/invalidez del resultado y error del servicio. OpenAI se simula; la calidad y disponibilidad del modelo requieren una prueba con una clave válida.

Consulta `AURORA.md` para mantener el diseño. El archivo de entrada en Streamlit Cloud sigue siendo `app.py`.
