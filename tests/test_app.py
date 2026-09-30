from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_provider_failure_survives_rerun_and_success_clears_it(monkeypatch):
    fake = ModuleType("ai_shopping_agent.agent")
    fake.agent = Mock()
    fake.agent.invoke.side_effect = RuntimeError("provider detail should stay in logs")
    monkeypatch.setitem(sys.modules, "ai_shopping_agent.agent", fake)
    app = AppTest.from_file(str(APP)).run()
    app.chat_input[0].set_value("Find organic honey").run()
    assert not app.exception
    assert "could not complete" in app.error[0].value
    assert "provider detail" not in app.error[0].value
    app.run()
    assert app.error
    fake.agent.invoke.side_effect = None
    fake.agent.invoke.return_value = {"messages": [SimpleNamespace(content="Organic Raw Honey costs $12.")]}
    app.chat_input[0].set_value("Try searching again").run()
    assert not app.exception
    assert not app.error
    assert app.session_state["messages"][-1]["content"] == "Organic Raw Honey costs $12."


def test_image_failure_remains_visible_and_removes_temporary_upload(monkeypatch, tmp_path):
    fake = ModuleType("ai_shopping_agent.agent")
    fake.agent = Mock()
    fake.agent.invoke.side_effect = TimeoutError("simulated vision timeout")
    monkeypatch.setitem(sys.modules, "ai_shopping_agent.agent", fake)
    upload = tmp_path / "product.png"
    upload.write_bytes(b"mock image; model call is replaced")
    app = AppTest.from_file(str(APP))
    app.session_state["messages"] = [
        {"role": "user", "content": f"I uploaded a product image. Image path: {upload}"}
    ]
    app.session_state["pending_image"] = "product.png"
    app.session_state["pending_image_path"] = str(upload)
    app.run()
    assert not app.exception
    assert "could not complete" in app.error[0].value
    assert not upload.exists()
    assert "pending_image_path" not in app.session_state
    assert len(app.session_state["messages"]) == 1
    app.run()
    assert app.error
    assert fake.agent.invoke.call_count == 1
