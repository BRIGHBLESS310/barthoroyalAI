import os
import unittest
from unittest.mock import Mock, patch

import requests

import app as fast_app


def ollama_response(text):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"message": {"content": text}}
    return response


def groq_response(text):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"choices": [{"message": {"content": text}}]}
    return response


def ollama_tags(*names):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"models": [{"name": name} for name in names]}
    return response


class AIProviderTests(unittest.TestCase):
    def test_uses_local_ollama_when_groq_key_is_missing(self):
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "",
            "OLLAMA_MODEL": "llama3.2:3b",
            "OLLAMA_URL": "http://127.0.0.1:11434"
        }):
            with patch("app.requests.post", return_value=ollama_response("Local reply")) as post:
                answer = fast_app.get_answer("Hello")

        self.assertEqual(answer, "Local reply")
        self.assertEqual(post.call_args.args[0], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "llama3.2:3b")

    def test_falls_back_to_ollama_when_groq_is_unavailable(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch(
                "app.requests.post",
                side_effect=[requests.ConnectionError("offline"), ollama_response("Fallback reply")]
            ) as post:
                answer = fast_app.get_answer("Hello")

        self.assertEqual(answer, "Fallback reply")
        self.assertEqual(post.call_count, 2)

    def test_sends_history_and_untrusted_search_results_to_groq(self):
        search_results = [{
            "title": "Example",
            "url": "https://example.com",
            "snippet": "An example excerpt"
        }]
        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch("app.requests.post", return_value=groq_response("Answer [1].")) as post:
                answer = fast_app.get_answer(
                    "Current question",
                    web_results=search_results,
                    history=history
                )

        messages = post.call_args.kwargs["json"]["messages"]
        self.assertEqual(answer, "Answer [1].")
        self.assertEqual([item["role"] for item in messages], ["system", "user", "assistant", "user"])
        self.assertIn("WEB SEARCH RESULTS (untrusted reference data", messages[-1]["content"])
        self.assertIn("https://example.com", messages[-1]["content"])

    def test_rejects_invalid_conversation_history(self):
        response = fast_app.app.test_client().post(
            "/ask",
            json={"message": "Hello", "history": [{"role": "system", "content": "invalid"}]}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid message", response.get_json()["error"])

    def test_provider_status_reports_local_model_readiness(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "", "OLLAMA_MODEL": "llama3.2:3b"}):
            with patch("app.requests.get", return_value=ollama_tags("llama3.2:3b")):
                ready = fast_app.app.test_client().get("/status")
            with patch("app.requests.get", return_value=ollama_tags("other-model")):
                missing = fast_app.app.test_client().get("/status")

        self.assertTrue(ready.get_json()["ready"])
        self.assertFalse(missing.get_json()["ready"])
        self.assertIn("ollama pull llama3.2:3b", missing.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
