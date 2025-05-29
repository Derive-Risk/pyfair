"""This module contains rudementary calculation logic."""

import numpy as np
import pandas as pd


class FairCalculations(object):
    """A captive class to perform calculations

    This class is called via the FairModel in which it is contained via its
    calculate() method. It then returns a series that is transformed via
    1) a step function followed by an average, 2) an addition function, or
    3) a multiplication function.

    """

    def __init__(self):
        # Lookup table for functions (no leaf nodes required)
        self._function_dict = {
            "Risk": self._calculate_multiplication,
            "Loss Event Frequency": self._calculate_multiplication,
            "Threat Event Frequency": self._calculate_multiplication,
            "Vulnerability": self._calculate_step_average,
            "Loss Magnitude": self._calculate_addition,
            "Primary Loss": self._calculate_multiplication,
            "Secondary Loss": self._calculate_multiplication,
        }

    def calculate(self, parent_name, child_1_data, child_2_data):
        """General function for dispatching calculations

        Parameters
        ----------
        parent_name : str
            A string describing a node, which is used with the
            _function_dict member to look up the appropriate function.

        child_1_data : pd.Series
            An input vector that is combined with child_2_data with a step,
            addtion, or multiplication function.

        child_2_data : pd.Series
            An input vector that is combined with child_1_data with a step,
            addtion, or multiplication function.

        .. warning:: the order of child_1_data and child_2_data does not
            matter for addition or multiplication, but it does for the
            stepwise function.

        Returns
        -------
        pd.Series
            A single series that is the product of the child data inputs
            and the function chose by the parent_name.

        """
        target_function = self._function_dict[parent_name]
        calculated_result = target_function(child_1_data, child_2_data)
        return calculated_result

    def _calculate_step_average(self, child_1_data, child_2_data):
        """Return per-simulation boolean (as float) for Vulnerability: 1.0 if TC > CS, else 0.0"""
        # Get Trues (1) where child_2 (TCap) is greater than child_1 (CS)
        bool_series = (child_1_data < child_2_data).astype(float)
        # Return the per-simulation result as a Series
        vuln = pd.Series(data=bool_series.values, index=bool_series.index)
        return vuln

    def _calculate_addition(self, child_1_data, child_2_data):
        """Calculate sum of two columns"""
        return child_1_data + child_2_data

    def _calculate_multiplication(self, child_1_data, child_2_data):
        """Calculate product of two columns"""
        return child_1_data * child_2_data
