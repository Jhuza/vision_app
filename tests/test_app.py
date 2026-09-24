"""Offline interaction tests: no API keys or paid requests are used."""
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from PIL import Image
from streamlit.testing.v1 import AppTest
import openai
import streamlit as st

APP = Path(__file__).resolve().parents[1] / "app.py"


def picture(name="test.png", color="blue"):
    image = io.BytesIO()
    Image.new("RGB", (8, 8), color).save(image, format="PNG")
    image.name = name
    image.seek(0)
    return image


def test_empty_page_and_validation_do_not_create_client(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(openai, "OpenAI", client)
    app = AppTest.from_file(str(APP)).run()
    assert not app.exception
    assert app.text_input[0].proto.type == app.text_input[0].proto.PASSWORD
    app.button[0].click().run()
    assert "clave" in app.warning[0].value
    app.text_input[0].set_value("offline-test-key").run()
    app.button[0].click().run()
    assert "imagen" in app.warning[0].value
    client.assert_not_called()


def test_image_context_stream_and_result_reset(monkeypatch):
    monkeypatch.setattr(st, "file_uploader", lambda *a, **kw: picture())
    client = MagicMock()
    chunks = [SimpleNamespace(choices=[])] + [SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=t))]) for t in [None, "Una ", "imagen azul."]]
    client.return_value.__enter__.return_value.chat.completions.create.return_value = chunks
    monkeypatch.setattr(openai, "OpenAI", client)
    app = AppTest.from_file(str(APP)).run()
    app.text_input[0].set_value("offline-test-key").run()
    app.toggle[0].set_value(True).run()
    app.text_area[0].set_value("¿Qué color aparece?").run()
    app.button[0].click().run()
    assert not app.exception and not app.error
    assert app.session_state["vision_response"] == "Una imagen azul."
    request = client.return_value.__enter__.return_value.chat.completions.create.call_args.kwargs
    assert request["model"] == "gpt-4o" and request["stream"] is True
    assert "¿Qué color aparece?" in request["messages"][0]["content"][0]["text"]
    assert request["messages"][0]["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")
    app.run()
    assert app.session_state["vision_response"] == "Una imagen azul."
    app.text_area[0].set_value("Otra pregunta").run()
    assert "vision_response" not in app.session_state
    client.return_value.__enter__.return_value.chat.completions.create.side_effect = RuntimeError("Servicio no disponible")
    app.button[0].click().run()
    assert "Servicio no disponible" in app.error[0].value
    assert "vision_response" not in app.session_state


def test_changing_image_clears_old_result(monkeypatch):
    monkeypatch.setattr(st, "file_uploader", lambda *a, **kw: picture())
    app = AppTest.from_file(str(APP)).run()
    app.session_state["vision_response"] = "Previous result"
    monkeypatch.setattr(st, "file_uploader", lambda *a, **kw: picture(color="red"))
    app.run()
    assert "vision_response" not in app.session_state
