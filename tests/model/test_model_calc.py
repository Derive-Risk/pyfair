import unittest

import numpy as np
import pandas as pd

from pyfair.model.model_calc import FairCalculations


class TestFairModelCalc(unittest.TestCase):

    # Raw data
    _CHILD_1_DATA = pd.Series([1, 2, 3, 4, 5])
    _CHILD_2_DATA = pd.Series([5, 4, 3, 2, 1])
    _MULT_OUTPUT = pd.Series([5, 8, 9, 8, 5])
    _ADD_OUTPUT = pd.Series([6, 6, 6, 6, 6])
    _STEP_OUTPUT = pd.Series([1, 1, 0, 0, 0], dtype=float)

    # Keys
    _MULTIPLICATION_ITEMS = [
        "Risk",
        "Loss Event Frequency",
        "Threat Event Frequency",
        "Primary Loss",
        "Secondary Loss",
    ]
    _ADDITION_ITEMS = ["Loss Magnitude"]
    _STEP_ITEMS = ["Vulnerability"]

    def setUp(self):
        self._calc = FairCalculations()

    def tearDown(self):
        self._calc = None

    def test_multiplication(self):
        """Test multiplication keywords and functions"""
        for key in self._MULTIPLICATION_ITEMS:
            result = self._calc.calculate(key, self._CHILD_1_DATA, self._CHILD_2_DATA)
            self.assertTrue(result.equals(self._MULT_OUTPUT))

    def test_addition(self):
        """Test addition keywords and functions"""
        for key in self._ADDITION_ITEMS:
            result = self._calc.calculate(key, self._CHILD_1_DATA, self._CHILD_2_DATA)
            self.assertTrue(result.equals(self._ADD_OUTPUT))

    def test_step_average(self):
        """Test step function keywords and functions"""
        for key in self._STEP_ITEMS:
            result = self._calc.calculate(key, self._CHILD_1_DATA, self._CHILD_2_DATA)
            self.assertTrue(result.equals(self._STEP_OUTPUT))


if __name__ == "__main__":
    unittest.main()
