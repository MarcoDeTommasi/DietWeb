import unittest
from types import SimpleNamespace
from unittest.mock import patch

from dietapp.meal_assistant import (
    alternatives_notice,
    assistant_context,
    build_system_prompt,
    generate_reply,
    initial_request,
)


class MealAssistantTests(unittest.TestCase):
    def setUp(self):
        self.meal = {
            "pasta_integrale": {"Quantità": 80, "Unità": "g"},
            "pollo": {"Quantità": 150, "Unità": "g"},
        }
        self.alternatives = [
            {
                "group_name": "Carboidrati",
                "food_name": "pasta_integrale",
                "quantity": 80,
                "unit": "g",
            },
            {
                "group_name": "Carboidrati",
                "food_name": "riso",
                "quantity": 100,
                "unit": "g",
            },
            {
                "group_name": "Gruppo non pertinente",
                "food_name": "latte",
                "quantity": 200,
                "unit": "ml",
            },
            {
                "group_name": "Gruppo non pertinente",
                "food_name": "yogurt",
                "quantity": 150,
                "unit": "g",
            },
        ]

    def test_context_only_includes_groups_relevant_to_meal(self):
        context = assistant_context("Lunedì", self.meal, self.alternatives)
        self.assertIn("Carboidrati", context["alternative_groups"])
        self.assertNotIn("Gruppo non pertinente", context["alternative_groups"])

    def test_notice_identifies_missing_coverage(self):
        context = assistant_context("Lunedì", self.meal, self.alternatives)
        notice = alternatives_notice(context)
        self.assertIn("Pollo", notice)

    def test_prompt_forbids_invented_equivalences(self):
        context = assistant_context("Lunedì", self.meal, self.alternatives)
        prompt = build_system_prompt(context)
        self.assertIn("Non inventare equivalenze", prompt)
        self.assertIn("pasta_integrale", prompt)
        self.assertIn("Riso", prompt)
        self.assertIn("equivalenze disponibili", initial_request("alternative"))

    @patch("dietapp.meal_assistant._client")
    def test_generate_reply_uses_shared_history(self, mocked_client):
        mocked_client.return_value.chat.completions.create.return_value = (
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Preparazione proposta")
                    )
                ]
            )
        )
        context = assistant_context("Lunedì", self.meal, self.alternatives)
        history = [
            {"role": "user", "content": "Preparami il pranzo"},
            {"role": "assistant", "content": "Prima risposta"},
            {"role": "user", "content": "Ora dammi una variante"},
        ]
        reply = generate_reply(context, history)
        self.assertEqual(reply, "Preparazione proposta")
        sent_messages = mocked_client.return_value.chat.completions.create.call_args.kwargs[
            "messages"
        ]
        self.assertEqual(sent_messages[-3:], history)


if __name__ == "__main__":
    unittest.main()
