import unittest

from dietapp.alternatives import alternative_coverage, validate_alternative_rows


class AlternativeTests(unittest.TestCase):
    def test_valid_groups_are_normalised(self):
        cleaned, errors = validate_alternative_rows(
            [
                {
                    "group_name": "Carboidrati pranzo",
                    "food_name": "Pasta integrale",
                    "quantity": 80,
                    "unit": "g",
                    "calories": 280,
                },
                {
                    "group_name": "Carboidrati pranzo",
                    "food_name": "Riso",
                    "quantity": 100,
                    "unit": "g",
                    "calories": 280,
                },
            ]
        )
        self.assertEqual(errors, [])
        self.assertEqual(cleaned[0]["food_name"], "pasta_integrale")
        self.assertEqual(cleaned[1]["quantity"], 100.0)

    def test_single_item_group_is_rejected(self):
        _, errors = validate_alternative_rows(
            [
                {
                    "group_name": "Proteine",
                    "food_name": "Pollo",
                    "quantity": 150,
                    "unit": "g",
                }
            ]
        )
        self.assertTrue(any("almeno due" in error for error in errors))

    def test_coverage_only_counts_linked_meal_foods(self):
        meal = {
            "pasta_integrale": {"Quantità": 80, "Unità": "g"},
            "pollo": {"Quantità": 150, "Unità": "g"},
        }
        alternatives = [
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
        ]
        coverage = alternative_coverage(meal, alternatives)
        self.assertEqual(coverage["covered"], ["pasta_integrale"])
        self.assertEqual(coverage["missing"], ["pollo"])
        self.assertFalse(coverage["complete"])


if __name__ == "__main__":
    unittest.main()
