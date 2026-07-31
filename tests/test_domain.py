import unittest

from dietapp.domain import (
    aggregate_requirements,
    build_shopping_list,
    empty_diet,
    normalise_food_name,
    validate_diet,
)


class DomainTests(unittest.TestCase):
    def test_food_normalisation(self):
        self.assertEqual(normalise_food_name("  Caffè d'Orzo  "), "caffe_d_orzo")

    def test_empty_diet_requires_at_least_one_food(self):
        self.assertEqual(len(validate_diet(empty_diet())), 1)

    def test_validation_rejects_zero_quantity(self):
        diet = empty_diet()
        diet["Lunedì"]["Pranzo"]["pasta"] = {"Quantità": 0, "Unità": "g"}
        errors = validate_diet(diet)
        self.assertTrue(any("quantità non valida" in error for error in errors))

    def test_requirements_keep_different_units_separate(self):
        diet = empty_diet()
        diet["Lunedì"]["Colazione"]["frutta"] = {"Quantità": 1, "Unità": "pz"}
        diet["Lunedì"]["Pranzo"]["frutta"] = {"Quantità": 200, "Unità": "g"}
        required = aggregate_requirements(diet, ["Lunedì"])
        self.assertEqual(required[("frutta", "pz")], 1)
        self.assertEqual(required[("frutta", "g")], 200)

        shopping = build_shopping_list(
            required, {("frutta", "pz"): 1, ("frutta", "g"): 50}
        )
        self.assertNotIn("frutta::pz", shopping)
        self.assertEqual(shopping["frutta::g"]["Quantità"], 150)


if __name__ == "__main__":
    unittest.main()
