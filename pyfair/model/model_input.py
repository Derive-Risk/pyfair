"""This module contains an input object for sanitizing / checking data."""

import scipy.stats

import numpy as np
import pandas as pd

from ..utility.fair_exception import FairException
from ..utility.beta_pert import FairBetaPert


class FairDataInput(object):
    """A captive class for checking and routing data inputs.

    An instance of this class is created when a FairModel is instantiated.
    It is used during the lifetime of the FairModel to take inputs, raise
    errors if the inputs are improper, route those inputs to the
    appropriate functions, and then create random variates using the
    keywords supplied.

    The shape of the distribution for the random variates is inferred from
    the keywords (self._parameter_map), and the restrictions around whether
    numbers are inferred from the the targets (self._le_1_targets). These
    are both analyzed when an external actor triggers generate(). Other
    checks are run as necessary.

    All the inputs for a model are stored in the self._supplied_values
    dictionary, which is important because it is the only record of what
    is stored when converting to JSON or another serialization format.

    """

    def __init__(self):
        # These targets must be less than or equal to one
        self._le_1_targets = [
            "Probability of Action",
            "Vulnerability",
            "Control Strength",
            "Threat Capability",
            "Secondary Loss Event Frequency",
        ]
        self._le_1_keywords = ["constant", "high", "mode", "low", "mean"]
        # Parameter map associates parameters with functions
        self._parameter_map = {
            "constant": self._gen_constant,
            "high": self._gen_pert,
            "mode": self._gen_pert,
            "low": self._gen_pert,
            "gamma": self._gen_pert,
            "mean": self._gen_normal,
            "stdev": self._gen_normal,
        }
        # List of keywords with function keys
        self._required_keywords = {
            self._gen_constant: ["constant"],
            self._gen_pert: ["low", "mode", "high"],
            self._gen_normal: ["mean", "stdev"],
        }
        # Storage of inputs
        self._supplied_values = {}

    def get_supplied_values(self):
        """Simple getter to return the supplied values

        Returns
        -------
        dict
            A dictionary of the values supplied to generate function. The
            keys for the dict will be the target node as a string (e.g.
            'Loss Event Frequency') and the values will be a sub-dictionary
            of keyword arguments ({'low': 50, 'mode}: 51, 'high': 52}).

        """
        return self._supplied_values

    def _check_le_1(self, target, **kwargs):
        """Raises error if not between one and zero"""
        # For every keyword argument
        for key, value in kwargs.items():
            # Set boolean conditions
            applicable_keyword = key in self._le_1_keywords
            applicable_target = target in self._le_1_targets
            # If key is in specified list
            if applicable_keyword and applicable_target:
                # Check if value is less than or equal to 1
                if 0.0 <= value <= 1.0:
                    pass
                # If not, raise error
                else:
                    raise FairException(
                        '"{}" must have "{}" value between zero and one.'.format(
                            target, key
                        )
                    )

    def _check_parameters(self, target_function, **kwargs):
        """Runs parameter checks

        This includes a determination that the value is equal to or
        greater than zero, and a check that all required keywords for a
        given

        """
        # Ensure all arguments are =< 0 where relevant
        for keyword, value in kwargs.items():
            # Two conditions
            value_is_less_than_zero = value < 0
            keyword_is_relevant = keyword in ["mean", "constant", "low", "mode", "high"]
            # Test conditions
            if keyword_is_relevant and value_is_less_than_zero:
                raise FairException('"{}" is less than zero.'.format(keyword))
        # Check that all required keywords are provided
        required_keywords = self._required_keywords[target_function]
        for required_keyword in required_keywords:
            if required_keyword in kwargs.keys():
                pass
            else:
                raise FairException(
                    '"{}" is missing "{}".'.format(
                        str(target_function), required_keyword
                    )
                )

    def generate(self, target, count, **kwargs):
        """Executes request, records parameters, and return random values

        More specifically this triggers the `_generate_single()`
        subroutine, records the appropriate keywords in the
        `_supplied_values` member, and returns a pandas Series of random
        values.

        Parameters
        ----------
        target : str
            The node for which the data is being generated (e.g. "Loss
            Event Frequency").
        count : int
            The number of random numbers generated (or alternatively, the
            length of the Series returned).
        **kwargs
            Keyword arguments with one of the following values: {`mean`,
            `stdev`, `low`, `mode`, `high`, `gamma`, or `constant`}.

        Raises
        ------
        pyfair.utility.fair_exception.FairException
            Raised if subroutine errors bubble up for reasons such as: 1)
            parameters are missing/incompatible, 2) parameters do not fall
            within proscribed value ranges, or 3) numbers supplied cannot
            be used to create meaningful distributions.

        Returns
        -------
        pd.Series
            A series of length `count` composed of random values. These
            values are consistent with a particular distribution type
            (Normal, BetaPert, or constant).

        """
        # Generate result
        result = self._generate_single(target, count, **kwargs)
        # Explicitly insert optional keywords for model storage
        dict_keys = kwargs.keys()
        if "low" in dict_keys and "gamma" not in dict_keys:
            kwargs["gamma"] = 4
        # Record and return
        self._supplied_values[target] = {**kwargs}
        return result

    def _generate_single(self, target, count, **kwargs):
        """Internal workhorse function for single request

        Where applicable this includes a check that parameters are less
        than or equal to one, determines the appropriate RNG funtion,
        checks the parameters for that function, clips the value range
        of the result of the RNG function, and returns the result.

        """
        # If destined for a le_1_target, check validity.
        if target in self._le_1_targets:
            self._check_le_1(target, **kwargs)
        # Otherwise figure out what function
        func = self._determine_func(**kwargs)
        # Check to make sure sufficient parameters exist
        self._check_parameters(func, **kwargs)
        # Run the function
        results = func(count, **kwargs)
        # Clip if in le_1_targets
        if target in self._le_1_targets:
            results = np.clip(results, 0.0, 1.0)
        # Otherwise ensure simply above zero
        else:
            results = np.clip(results, 0.0, np.inf)
        return results

    def generate_multi(self, prefixed_target, count, kwargs_dict):
        """Generates aggregate risk data for multiple targets

        .. deprecated:: 0.1-alpha.1
           `generate_multi()` will be removed in future versions because
           it was a terrible idea to begin with.

        This function essentially creates a small simulation for each key
        in the dictionary. For example, with the following data:

        .. code:: python

            {
                'Reputational': {
                    'Secondary Loss Event Frequency': {'constant': 4000},
                    'Secondary Loss Event Magnitude': {
                        'low': 10, 'mode': 20, 'high': 100
                    },
                },
                'Legal': {
                    'Secondary Loss Event Frequency': {'constant': 2000},
                    'Secondary Loss Event Magnitude': {
                        'low': 10, 'mode': 20, 'high': 100
                    },
                }
            }

        Two separate simulations for "Reputational" and "Legal" will be run
        using the information supplied. Each of these simulations will be
        composed of random values with distributions based on the
        parameters supplied. Those simulations are then calculated
        independently, and then summed to yield aggregate risk.

        .. warning:: unlike other functions, this does not take **kwargs--
           rather it takes a dictionary

        Parameters
        ----------
        prefixed_target : str
            The node for which the data is being generated (e.g. "Loss
            Event Frequency").
        count : int
            The number of random numbers generated (or alternatively, the
            length of the Series returned).
        kwargs_dict : dict
            This is an actual dictionary (and not an expanded **kwargs)
            keyword list.

        Raises
        ------
        pyfair.utility.fair_exception.FairException
            Raised if subroutine errors bubble up for reasons such as: 1)
            parameters are missing/incompatible, 2) parameters do not fall
            within proscribed value ranges, or 3) numbers supplied cannot
            be used to create meaningful distributions.

        Returns
        -------
        pd.Series
            A series of length `count` composed of aggregate risk dollar
            amounts.

        """
        # Remove prefix from target
        final_target = prefixed_target.lstrip("multi_")
        # Create a container for dataframes
        df_dict = {target: pd.DataFrame() for target in kwargs_dict.keys()}
        # For each target
        for target, column_dict in kwargs_dict.items():
            # For each column in that target
            for column, params in column_dict.items():
                # Gen data
                data = self._generate_single(target, count, **params)
                s = pd.Series(data)
                # Put in dict
                df_dict[target][column] = s
        # Get partial secondary losses and sum up all the values
        summed = sum(df.prod(axis=1) for df in df_dict.values())
        # Record params
        new_target = "multi_" + final_target
        self._supplied_values[new_target] = kwargs_dict
        return summed

    def supply_raw(self, target, array):
        """Supply raw data to the model

        This takes an arbitrary array, runs some quick checks, and returns
        the array if appropriate.

        Parameters
        ----------
        target : str
            The eventual target of the raw data
        array : list, pd.Series, or array
            The raw data being supplied

        Returns
        =======
        np.array
            The data for the model

        Raises
        ------
        pyfair.utility.fair_exception.FairException
            Raised if the data has null values

        """
        # Ensure numeric
        clean_array = pd.to_numeric(array)
        # Coerce to series
        if type(array) == pd.Series:
            s = pd.Series(clean_array.values)
        else:
            s = pd.Series(clean_array)
        # Check numeric and not null
        if s.isnull().any():
            raise FairException("Supplied data contains null values")
        # Ensure values are appropriate
        if target in self._le_1_targets:
            if s.max() > 1 or s.min() < 0:
                raise FairException(f"{target} data greater or less than one")
        self._supplied_values[target] = {"raw": s.values.tolist()}
        return s.values

    def _determine_func(self, **kwargs):
        """Checks keywords and returns the appropriate function object."""
        # Check whether keys are recognized
        for key in kwargs.keys():
            if key not in self._parameter_map.keys():
                raise FairException('"{}"" is not a recognized keyword'.format(key))
        # Check whether all keys go to same function via set comprension
        functions = list(set([self._parameter_map[key] for key in kwargs.keys()]))
        if len(functions) > 1:
            raise FairException(
                '"{}" mixes incompatible keywords.'.format(str(kwargs.keys()))
            )
        else:
            function = functions[0]
            return function

    def _gen_constant(self, count, **kwargs):
        """Generates constant array of size `count`"""
        return np.full(count, kwargs["constant"])

    def _gen_normal(self, count, **kwargs):
        """Geneates random normally-distributed array of size `count`"""
        normal = scipy.stats.norm(loc=kwargs["mean"], scale=kwargs["stdev"])
        rvs = normal.rvs(count)
        return rvs

    def _gen_pert(self, count, **kwargs):
        """Checks parameters, creates BetaPert, returns random values"""
        self._check_pert(**kwargs)
        pert = FairBetaPert(**kwargs)
        rvs = pert.random_variates(count)
        return rvs

    def _check_pert(self, **kwargs):
        """Does the work of ensuring BetaPert distribution is valid"""
        conditions = {
            "mode >= low": kwargs["mode"] >= kwargs["low"],
            "high >= mode": kwargs["high"] >= kwargs["mode"],
        }
        for condition_name, condition_value in conditions.items():
            if condition_value == False:
                err = 'Param "{}" fails PERT requirement "{}".'.format(
                    kwargs, condition_name
                )
                raise FairException(err)
