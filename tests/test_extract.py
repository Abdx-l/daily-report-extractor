import unittest
from extract import extract, score


class ExtractTests(unittest.TestCase):
    def test_valid_and_accuracy(self):
        result = extract("Date: 2026-10-21\nWeather: Rain\nCrew: 4\nHours: 8\nDelay: none")
        self.assertEqual(result["errors"], [])
        self.assertEqual(score(result, {"date":"2026-10-21","weather":"Rain","crew":4,"hours":8.0,"delay":"none"})["accuracy"], 1)

    def test_invalid_values_flag_review(self):
        result = extract("Date: tomorrow\nCrew: -2\nHours: 25", ocr=True)
        self.assertTrue(result["review"])
        self.assertEqual(len(result["errors"]), 4)

