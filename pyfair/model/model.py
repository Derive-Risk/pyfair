"""This module contains the main class for creating FAIR models."""

import datetime
import json
import uuid

import numpy as np
import pandas as pd

from .model_input import FairDataInput
from .model_tree import FairDependencyTree
from .model_calc import FairCalculations
from ..utility.fair_exception import FairException


class FairModel(object):
    """A main class to act as an API for FAIR Model construction.

    A single instance of this class is created for each FAIR model. It
    contains a dependency resolution tree (self._tree), a calculation
    member (self._calculation), and an input parser (self._input). 

    Calculations are strucutred as a series of connected nodes, with
    one node for each of the potential FAIR inputs. A user interacts
    with this class by loading data via JSON or by inputting data
    for the individual nodes. The user then triggers the
    calculate_all() method to run all the subcalculations necessary
    to complete the FAIR model.

    Parameters
    ----------
    name : str
        A human-readable designation for identification
    n_simulations : int, optional
        Number of simulations created (default is 10,000)
    random_seed : int, optional
        Random seed for number generation (default is 42)
    model_uuid : str, optional
        uuid.uuid4 string (default is None, meaning one will be assigned)
    creation_date : str, optional
        Creation date (default is None, meaning one will be assigned)

    Examples
    --------
    >>> model = pyfair.model.FairModel(name='Data Loss')
    >>> model.input_data('Loss Magnitude', mean=20, stdev=10)
    >>> model.input_data('Loss Event Frequency', constant=5)
    >>> model.calculate_all()
    >>> model.export_results()

    .. warning:: Do not supply your own UUID/creation date unless
        you want to break things.

    """

    ##########################################################################
    # Creation Methods
    ##########################################################################

    def __init__(self, 
                 name, 
                 n_simulations=10_000, 
                 random_seed=42, 
                 model_uuid=None, 
                 creation_date=None):
        # Set n_simulations and random seed for reproducablility
        self._name = name
        self._n_simulations = n_simulations
        # Do not change the random_seed unless you have a good reason.
        self._random_seed = random_seed
        np.random.seed(random_seed)
        # Instantiate components
        self._model_table = pd.DataFrame(columns=[
            'Risk',
            'Loss Event Frequency',
            'Threat Event Frequency',
            'Vulnerability',
            'Contact Frequency',
            'Probability of Action',
            'Threat Capability',
            'Control Strength',
            'Loss Magnitude',
            'Primary Loss',
            'Secondary Loss',
            'Secondary Loss Event Frequency',
            'Secondary Loss Event Magnitude',
        ])
        self._data_input  = FairDataInput() 
        self._tree        = FairDependencyTree()
        self._calculation = FairCalculations()
        # If no ID supplied, create.
        if model_uuid and creation_date:
            self._model_uuid  = model_uuid
            self._creation_date = creation_date
        else:
            self._model_uuid = str(uuid.uuid1())
            self._creation_date = str(datetime.datetime.now())
        # Standardized targets for abbreviation use
        self._target_map = {
            'LEF' : 'Loss Event Frequency',
            'TEF' : 'Threat Event Frequency',
            'V'   : 'Vulnerability',
            'C'   : 'Contact Frequency',
            'A'   : 'Probability of Action',
            'TC'  : 'Threat Capability',
            'CS'  : 'Control Strength',
            'LM'  : 'Loss Magnitude',
            'PL'  : 'Primary Loss',
            'SL'  : 'Secondary Loss',
            'SLEF': 'Secondary Loss Event Frequency',
            'SLEM': 'Secondary Loss Event Magnitude',
        }
        # Add lowercase versions to target map
        self._target_map.update({
            key.lower(): value
            for key, value
            in self._target_map.items()
        })

    @staticmethod
    def read_json(param_json):
        """Static method to create a model from a JSON string

        Parameters
        ----------
        param_json : str
            a UTF-8 encoded JSON string containing model data

        Returns
        -------
        pyfair.model.FairModel
            A model instance using the JSON parameters supplied

        Raises
        ------
        pyfair.fair_exception.FairException
            If metamodel JSON is supplied erroneously

        Example
        -------
        >>> with open('serialized_model.json') as f:
        ...     json_text = f.read()
        ...
        >>> model = FairModel.read_json(json_text)

        """
        data = json.loads(param_json)
        # Check type of JSON
        if data['type'] != 'FairModel':
            raise FairException('Failed JSON parse attempt. This is not a FairModel.')
        model = FairModel(
            name=data['name'],
            n_simulations=data['n_simulations'], 
            random_seed=data['random_seed'],
            model_uuid=data['model_uuid'],
            creation_date=data['creation_date']
        )
        # Be lazy
        drop_params = [
            'name',
            'n_simulations', 
            'random_seed', 
            'creation_date', 
            'model_uuid',
            'type'
        ]
        # Load params one-by-one.
        for param_name, param_value in data.items():
            # If it's not in the drop list, load it.
            if param_name not in drop_params:
                # Input params must be treated differently if raw
                contains_raw = 'raw' in param_value.keys()
                if param_name.startswith('multi'):
                    model.input_multi_data(param_name, param_value)
                # Raw needs a different way
                elif contains_raw:
                    model.input_raw_data(param_name, param_value['raw'])
                # Otherwise standard input
                else:
                    model.input_data(param_name, **param_value)
        # Calculate
        model.calculate_all()
        return model

    #######################################################################
    # Inspection Methods
    #######################################################################
    #
    # <screed>
    #    I know. I know. Getters and setters have no place in Python.
    #    That said ... if it's public people will read AND write it.
    #    We definitely don't want people writing to params.
    #    We could wrap a decorator allowing setting, but that's overkill.
    #    It's better to just have a simple export function.
    # </screed>
    #
    #######################################################################

    def get_node_statuses(self):
        """Public method access private node status information in ._tree

        Returns
        -------
        pandas.Series
            A series with index of nodes, and values of statuses 

        """
        return self._tree.get_node_statuses()

    def get_name(self):
        """Gives the name of the model

        Returns
        -------
        str
            Name of model

        """
        return self._name

    def get_uuid(self):
        """Returns the model's unique ID.

        Returns
        -------
        str
            The UUID of the model.

        """
        return self._model_uuid

    def calculation_completed(self):
        """Public method to check completion status of dependency tree

        Returns
        -------
        bool
            Whether the calculation dependencies are satisfied

        """
        status = self._tree.calculation_completed()
        return status

    ##########################################################################
    # Input methods
    ##########################################################################

    def input_data(self, target, **kwargs):
        """Input data for a single node

        This takes input, feeds it to self._data_input.generate(), and
        updates the dependencies via self._tree.update_status(). The kwargs
        can be for normal (keywords `mean` and `stdev`), BetaPert (keywords
        `low`, `mode`, `high`, and `gamma`), , or a constant (keywords 
        `constant`).

        Parameters
        ----------
        target : str
            The name of the node for which the arguments are directed
        kwargs : float
            The arguments used to generate a distribution for the node

        Returns
        -------
        pyfair.model.FairModel
            A reference to this object of type FairModel

        Examples
        --------
        >>> model = pyfair.model.FairModel(name='Data Loss')
        >>> model.input_data('Loss Magnitude', mean=20, stdev=10)

        """
        # Standardize inputs to account for abbreviations
        target = self._standardize_target(target)
        # Generate data via data captive class
        data = self._data_input.generate(target, self._n_simulations, **kwargs)
        # Update dependency tracker captive class
        self._tree.update_status(target, 'Supplied')
        # Update the model table with the generated data
        self._model_table[target] = data
        return self

    def input_multi_data(self, target, kwargs_dict):
        """Input data for multiple items that roll up into an aggregate

        As of now, this is only used for Secondary Loss when calculating
        mutliple secondary loss line items (e.g. 'Reputation' has a
        probability of A and a loss of B; 'Morale' has a probability
        of C and a loss of D, etc.).

        Parameters
        ----------
        target : str
            The name of the node for which the arguments are directed
        kwargs_dict : dict
            The arguments used to generate a distribution for the node

        Returns
        -------
        pyfair.model.FairModel
            A reference to this object of type FairModel

        Examples
        --------
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model1.input_multi_data('Secondary Loss', {
        ...     'Reputational': {
        ...         'Secondary Loss Event Frequency': {'constant': 4000},
        ...         'Secondary Loss Event Magnitude': {'low': 10, 'mode': 20, 'high': 100},
        ...     },
        ...     'Legal': {
        ...         'Secondary Loss Event Frequency': {'constant': 2000},
        ...         'Secondary Loss Event Magnitude': {'low': 10, 'mode': 20, 'high': 100},        
        ...     }
        ... })

        """
        # Generate our data
        data = self._data_input.generate_multi(target, self._n_simulations, kwargs_dict)
        # Multitargets are prefixed with 'multi_'
        mod_target = target.lstrip('multi_')
        # Supplied then calculated is a nasty workaround to propegate down then change.
        self._tree.update_status(mod_target, 'Supplied')
        self._tree.update_status(mod_target, 'Calculated')
        # Update model table with data
        self._model_table[mod_target] = data
        return self

    def bulk_import_data(self, param_dictionary):
        """Takes multiple inputs via nested dictionaries.

        The function iterates through a dictionary and runs input_data()
        for each item. This allows for multiple items to be added at a 
        single time. The param dictionary will take the form:

        {'target_1': {param_1: value_1}, 'target_2': {param_2: value_2}}

        Parameters
        ----------
        param_dictionary : dict
            A nested dictionary of parameters.

        Returns
        -------
        pyfair.model.FairModel
            A reference to this object of type FairModel

        Examples
        --------
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model.bulk_import_data({
        ...     'Loss Event Frequency': {'mean': 90, 'stdev': 100},
        ...     'Loss Magnitude': {'constant': 4000}, 
        ... })

        """
        # Iterate through each key, value pair and run through input_data()
        for target, parameters in param_dictionary.items():
            self.input_data(target, **parameters)
        return self

    def input_raw_data(self, target, array):
        """Supply a raw array to the model

        This function allows for arbitrary data to be placed within the
        model by passing an array.

        Parameters
        ----------
        target : str
            The node to which to send the data
        array : np.array, list, or pd.Series
            Raw input data for the model

        Returns
        -------
        pyfair.model.FairModel
            A reference to this object of type FairModel

        Raises
        ------
        FairException
            If an inappropriate number of items are supplied

        Examples
        --------
        >>> array = np.array([1,2,3])
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model.input_raw_data('Loss Magnitude', array)

        .. warning:: raw inputs can drastically increase the size of your
                     stored models. Because this raw data must be recorded
                     and cannot be simulated, it is stored in its entirity
                     within the model's JSON.

        """
        # Standardize inputs to account for abbreviations
        target = self._standardize_target(target)
        # Check types
        acceptable_types = [list, np.array, pd.Series]
        if type(array) not in acceptable_types:
            raise FairException('Inappropriate input type.')
        # Check length
        if len(array) != self._n_simulations:
            message = "Input legnth {}, but simulations count is is {}".format(
                len(array),
                self._n_simulations
            )
            raise FairException(message)
        # Generate data via data captive class
        data = self._data_input.supply_raw(target, array)
        # Update dependency tracker captive class
        self._tree.update_status(target, 'Supplied')
        # Update the model table with the generated data
        self._model_table[target] = data
        return self

    def _standardize_target(self, target):
        """A function to change target abbreviations into full names"""
        if target in self._target_map.keys():
            mapped_target = self._target_map[target]
        else:
            mapped_target = target
        return mapped_target

    ##########################################################################
    # Calculation methods
    ##########################################################################

    def calculate_all(self):
        """Runs all outstanding calculations for uncalculated nodes.

        This is done by obtaining a list of all 'calculable' nodes.
        If it is not ready for a complete calculation, it throws an
        error. It goes through all the calculable nodes and calculates
        them using the private _calculate_node() method.

        Raises
        ------
        pyfair.fair_exception.FairException
            Raised is complete calculation is impossible.

        Returns
        -------
        pyfair.model.FairModel
            A reference to this object of type FairModel

        Examples
        --------
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model.bulk_import_data({
        ...     'Loss Event Frequency': {'mean': 90, 'stdev': 100},
        ...     'Loss Magnitude': {'constant': 4000}, 
        ... })
        ... model.calculate_all()

        """
        # If required data has not been input, raise error
        ready_for_calculation = self._tree.ready_for_calculation()
        if not(ready_for_calculation):
            status_str = str(pd.Series(self._tree.get_node_statuses(), dtype='str'))
            raise FairException('Not ready for calculation. See statuses: \n{}'.format(status_str))
        status = pd.Series(self._tree.get_node_statuses(), dtype='str')
        # Needs to be string to avoid weird numpy error with empty status array
        # https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        calculable_nodes = (status.loc[status.astype(str) == 'Calculable']
                                  .index.values.tolist()
        )
        # Go through all the nodes and update them if possible.
        while calculable_nodes:
            # Avoid mutating while iterating.
            node_names = tuple(calculable_nodes)
            for node_name in node_names:
                # Calculate if possible
                self._calculate_node(node_name)
                # Remove node from list if calculated.
                if self._tree.nodes[node_name].status == 'Calculated':
                    calculable_nodes.remove(node_name)
        return self

    def _calculate_node(self, name):
        """Calculate node by checking parents and updating status"""
        # Alsias for data table
        data = self._model_table
        # Get child node statuses
        parent = self._tree.nodes[name]
        child_1, child_2 = parent.children
        child_1_ready = child_1.status in ['Calculated', 'Supplied']
        child_2_ready = child_2.status in ['Calculated', 'Supplied']
        # If children ready for calculation, calculate
        if child_1_ready and child_2_ready:
            # Order for vulnerability matters.
            if parent.name == 'Vulnerability':
                child_1_data = data['Control Strength']
                child_2_data = data['Threat Capability']
            # For others, it matters not.
            else:
                child_1_data = data[child_1.name]
                child_2_data = data[child_2.name]
            calculated_data = self._calculation.calculate(name, child_1_data, child_2_data)
            data[name] = calculated_data
            self._tree.update_status(name, 'Calculated')
        else:
            pass

    ##########################################################################
    # Export methods
    ##########################################################################

    def export_results(self):
        """Exports the result of the calculation as a dataframe

        Returns
        -------
        pandas.DataFrame
            A reference to this object of type FairModel

        Examples
        --------
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model.bulk_import_data({
        ...     'Loss Event Frequency': {'mean': 90, 'stdev': 100},
        ...     'Loss Magnitude': {'constant': 4000}, 
        ... })
        ... model.calculate_all)()
        ... results = model.export_results()

        """
        return self._model_table

    def to_json(self):
        """Dump the model as JSON string

        For an example, see the file: "serialized_model.json".

        Returns
        -------
        str
            A JSON string representing the model information.

        Examples
        --------
        >>> model = pyfair.FairModel(name="Insider Threat")
        >>> model.bulk_import_data({
        ...     'Loss Event Frequency': {'mean': 90, 'stdev': 100},
        ...     'Loss Magnitude': {'constant': 4000},
        ... })
        ... model.calculate_all)()
        ... json_data = model.to_json()

        """
        # Copy only.
        data = {**self._data_input.get_supplied_values()}
        # Add non-parameter metadata information
        data['name'] = str(self._name)
        data['n_simulations'] = self._n_simulations
        data['random_seed'] = self._random_seed
        data['model_uuid'] = self._model_uuid
        data['type'] = str(self.__class__.__name__)
        data['creation_date'] = self._creation_date
        # Dump as string
        json_data = json.dumps(
            data,
            indent=4,
        )
        return json_data

    def export_params(self):
        """Export params as a dictionary.

        Returns
        -------
        dict
            Non-metadata parameters

        """
        return self._data_input.get_supplied_values()
