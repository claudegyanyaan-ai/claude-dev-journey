import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main


class TestRunCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(main.run_calculator("add", 2, 3), 5)

    def test_divide_by_zero(self):
        self.assertEqual(main.run_calculator("divide", 10, 0), "Error: division by zero")

    def test_log_default_base(self):
        self.assertAlmostEqual(main.run_calculator("log", 100), 2)


if __name__ == "__main__":
    unittest.main()
