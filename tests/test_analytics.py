import unittest

import pandas as pd

from dietapp.analytics import filter_period, purchases_to_frame


class AnalyticsTests(unittest.TestCase):
    def test_records_are_flattened_and_invalid_rows_ignored(self):
        frame = purchases_to_frame(
            [
                {
                    "id": 1,
                    "data": "2026-01-10",
                    "lista_spesa": {
                        "pasta": {"Quantità": 100, "Unità": "g"},
                        "broken": {"Quantità": "no", "Unità": "g"},
                    },
                }
            ]
        )
        self.assertEqual(len(frame), 1)
        self.assertEqual(frame.iloc[0]["Alimento"], "pasta")

    def test_period_filter_works_across_year_boundary(self):
        frame = purchases_to_frame(
            [
                {
                    "id": 1,
                    "data": "2025-12-20",
                    "lista_spesa": {"pasta": {"Quantità": 100, "Unità": "g"}},
                },
                {
                    "id": 2,
                    "data": "2025-08-01",
                    "lista_spesa": {"pasta": {"Quantità": 100, "Unità": "g"}},
                },
            ]
        )
        result = filter_period(frame, 3, now=pd.Timestamp("2026-02-01"))
        self.assertEqual(result["Acquisto"].tolist(), [1])


if __name__ == "__main__":
    unittest.main()
