"""Base report class for creating HTML reports"""

import base64
import datetime
import getpass
import inspect
import io
import os
import pathlib

import numpy as np
import pandas as pd

from .. import VERSION

from .tree_graph import FairTreeGraph
from .distribution import FairDistributionCurve
from .exceedence import FairExceedenceCurves
from ..utility.fair_exception import FairException
from .violin import FairViolinPlot


class FairBaseReport(object):
    """A base class for creating FairModel and FairMetaModel reports

    This class exists to provide a common base for mutliple report types.
    It carries with it formatting data, file paths, and a variety of 
    methods for creating report components. It is not intended to be
    instantiated on its own.

    """
    def __init__(self, currency_prefix='$'):
        # Add formatting strings
        self._currency_prefix = currency_prefix
        self._model_or_models = None
        self._currency_format_string     = currency_prefix + '{0:,.0f}'
        self._float_format_string      = '{0:.2f}'
        self._format_strings = {
            'Risk'                           : self._currency_format_string,
            'Loss Event Frequency'           : self._float_format_string,
            'Threat Event Frequency'         : self._float_format_string,
            'Vulnerability'                  : self._float_format_string,         
            'Contact Frequency'              : self._float_format_string,
            'Probability of Action'          : self._float_format_string,
            'Threat Capability'              : self._float_format_string,
            'Control Strength'               : self._float_format_string,
            'Loss Magnitude'                 : self._currency_format_string,
            'Primary Loss'                   : self._currency_format_string,
            'Secondary Loss'                 : self._currency_format_string,
            'Secondary Loss Event Frequency' : self._float_format_string,
            'Secondary Loss Event Magnitude' : self._currency_format_string,
        }
        # Add locations
        self._fair_location = pathlib.Path(__file__).parent.parent
        self._static_location = self._fair_location / 'static'
        self._logo_location = self._static_location / 'white_python_logo.png'
        self._template_paths = {
            'css'   : self._static_location / 'fair.css',
            'simple': self._static_location / 'simple.html'
        }
        self._param_cols = [
            'low',
            'most_likely',
            'high',
            'constant',
            'mean',
            'stdev'
        ]

    def _input_check(self, value):
        """Check input value for report is appropriate
        Raises
        ------
        FairException
            If an inappropriate object or iterable of objects is supplied
        """
        # If it's a model or metamodel, plug it in a dict.
        rv = {}
        if value.__class__.__name__ in ['FairModel', 'FairMetaModel']:
            rv[value.get_name()] = value
            return rv
        # Check for iterable.
        if not hasattr(value, '__iter__'):
            raise FairException('Input is not a FairModel, FairMetaModel, or an iterable.')
        if len(value) == 0:
            raise FairException('Empty iterable where iterable of models expected.')
        # Iterate and process remainder.
        for proported_model in value:
            # Check if model
            if proported_model.__class__.__name__ in ['FairModel', 'FairMetaModel']:
                # Check if calculated
                if proported_model.calculation_completed():
                    rv[proported_model.get_name()] = proported_model
                else:
                    raise FairException('Model or FairModel has not been calculated.')
            else:
                raise FairException('Iterable member is not a FairModel or FairMetaModel')
        return rv

    def get_format_strings(self):
        """Returns the format strings for respective nodes
        Returns
        -------
        dict
            Containing keys with node names and values with the formatting
            string appropriate for those nodes
        """
        return self._format_strings

    def base64ify(self, image, alternative_text='', options=''):
        """Binary data into embeddable <img> tag with base64 data
        
        To avoid having separate image files, pyfair simply embeds report
        images as base64 image tags. base64ify() is a convenience function
        that creates these tags.
        image : [bytes, str, pathlib.Path]
            The binary data, path string, or pathlib.Path containing either
            the data itself or a file of data.
        
        alternative_text: str, optional
            Alternative text to be showed in the event the image does not
            properly render
        options : str, optional
            A string containing additional HTML attributes to be placed
            between "<image " and " src="
        Returns
        -------
        str
            An HTML <img> tag with base64 data and appropriate attributes
        Raises
        ------
        TypeError
            If the image parameter supplied is of an inappropriate type
        """
        # If path, open and read.
        if type(image) == str or isinstance(image, pathlib.Path):
            with open(image, 'rb') as f:
                binary_data = f.read()
        # If bytes, jsut write
        elif type(image) == bytes:
            binary_data = image
        else:
            raise TypeError(str(image) + ' is not a string, path, or bytes.')
        # Get base64 string
        base64_string = base64.b64encode(binary_data).decode('utf8')
        # Create tag
        tag = f'<img {options} src="data:image/png;base64, {base64_string}" alt="{alternative_text}"/>'
        return tag

    def _construct_output(self):
        """Stub to be overridden by subclass to generate report"""
        # Get report
        raise NotImplementedError()

    def to_html(self, output_path):
        """Writes HTML report data to a file
        This is a public method that simply obtains the output of the
        _construct_output() method and writes it to a file.
        Parameters
        ----------
        output_path : str or pathlib.Path
            The output path to which the HTML data is written
        """
        output = self._construct_output()
        with open(output_path, 'w+') as f:
            f.write(output)

    def _fig_to_img_tag(self, fig):
        """Converts matplotlib fig to base64 encoded img tag"""
        data = io.BytesIO()
        fig.savefig(data, format='png', transparent=True)
        data.seek(0)
        img_tag = self.base64ify(data.read())
        return img_tag

    def _get_data_table(self, model):
        """Takes model and gnerates HTML table from the model's results"""
        data = model.export_results().dropna(axis=1)
        table = data.to_html(
            border=0, 
            justify='left', 
            classes='fair_metadata_table'
        )
        return table

    def _get_parameter_table(self, model):
        """Visitorish function to inspect a model's parameters"""
        data = model.export_parameters()
        return data

    def _get_metadata_table(self):
        """Generate table of metadata to attach to top of model.
        Do not put model-specific data in here.
        """
        # Get username
        try:
            username = getpass.getuser()
        # The exception this throws is not conspicuously documented
        except Exception:
            username = 'Unknown'
        # Add metadata
        metadata = pd.Series({
            'Author': username,
            'Created': str(datetime.datetime.now()).partition('.')[0],
            'PyFair Version': VERSION,
            'Type': type(self).__name__
        }).to_frame().to_html(border=0, header=False, justify='left', classes='fair_metadata_table')
        return metadata

    def _get_tree(self, model):
        """Create base64 image string using FairTreeGraph"""
        ftg = FairTreeGraph(model, self._format_strings)
        fig, ax = ftg.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_distribution(self, model_or_models, currency_prefix):
        """Create base64 image string using FairDistributionCurve"""
        fdc = FairDistributionCurve(model_or_models, currency_prefix)
        fig, ax = fdc.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_distribution_icon(self, model, target):
        """Create base64 icon string using FairDistributionCurve"""
        fdc = FairDistributionCurve(model, self._currency_prefix)
        fig, ax = fdc.generate_icon(model.get_name(), target)        
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_exceedence_curves(self, model_or_models, currency_prefix):
        """Create base64 image string using FairExceedenceCurves"""
        fec = FairExceedenceCurves(model_or_models, currency_prefix)
        fig, ax = fec.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_violins(self, metamodel):
        """Create base64 image string using FairViolinPlot"""
        vplot = FairViolinPlot(metamodel)
        fig, ax = vplot.generate_image()
        img_tag = self._fig_to_img_tag(fig)
        return img_tag

    def _get_overview_table(self, model_or_models):
        """Create a risk overview table using a model or list of models"""
        # Get final Risk vectors for all models
        try:
            risk_results = pd.DataFrame({
                name: model.export_results()['Risk']
                for name, model 
                in model_or_models.items()
            })
        except KeyError:
            raise FairException("No 'Risk' key. Model likely uncalculated.")
        # Get aggregate statistics and set titles
        risk_results = risk_results.agg(['mean', 'std', 'min', 'max'])
        risk_results.index = ['Mean', 'Stdev', 'Minimum', 'Maximum']
        # Format risk results into dataframe
        overview_df = risk_results.applymap(lambda x: self._format_strings['Risk'].format(x))
        overview_df.loc['Simulations'] = [
            '{0:,.0f}'.format(len(model.export_results())) 
            for model
            in model_or_models.values()
        ]
        # Add data
        overview_df.loc['Identifier'] = [model.get_uuid() for model in model_or_models.values()]
        overview_df.loc['Model Type'] = [model.__class__.__name__ for model in model_or_models.values()]
        # Export df to HTML and return
        overview_html = overview_df.to_html(border=0, header=True, justify='left', classes='fair_table')
        return overview_html

    def _get_model_parameter_table(self, model):
        """Generate a table with parameter statistics and icons"""
        params = dict(**model.export_params())
        # Remove items we don't want.
        params = {
            key: value
            for key, value
            in params.items() 
            if key in self._format_strings.keys()
        }
        # Set up alias and dataframe
        fs = self._format_strings
        param_df = pd.DataFrame(params).T
        # For possible param column name
        for column in self._param_cols:
            # If the column is not present in param_df
            if column not in param_df.columns:
                # Add that column in with null data
                param_df[column] = np.nan
        # Create descriptive statistics from parameter df
        param_df = param_df[self._param_cols]
        param_df['mean'] = model.export_results().mean(axis=0)
        param_df['stdev'] = model.export_results().std(axis=0)
        param_df['min'] = model.export_results().min(axis=0)
        param_df['max'] = model.export_results().max(axis=0)
        # Transform param_df in place
        param_df = param_df.apply(
            lambda row: pd.Series(
                [
                    # ... by getting the format string and formatting
                    fs[row.name].format(item)
                    # For each item
                    for item
                    in row
                ],
                # And keep the index
                index=row.index.values
            ),
            # On a column basis
            axis=1,
        )
        param_df = param_df.applymap(lambda x: '' if 'nan' in x else x)
        # Do not truncate our base64 images.
        pd.set_option('display.max_colwidth', None)
        # Create our distribution icons as strings in table
        param_df['distribution'] = [
            self._get_distribution_icon(model, target)
            for target
            in param_df.index.values
        ]
        # Export table to html
        detail_table = param_df.to_html(
            border=0,
            header=True,
            justify='left',
            classes='fair_table',
            escape=False
        )
        return detail_table

    def _get_metamodel_parameter_table(self, metamodel):
        """Create table for metamodel"""
        # Create our table, transpose it, get descriptive statistics
        risk_df = metamodel.export_results().T
        risk_df = pd.DataFrame({
            'mean' : risk_df.mean(axis=1),
            'stdev': risk_df.std(axis=1),
            'min'  : risk_df.min(axis=1),
            'max'  : risk_df.max(axis=1),
            'geo_mean': risk_df.apply(lambda x: np.exp(np.mean(np.log(x[x > 0]))), axis=1),
            'mode': risk_df.mode(axis=1)[0],
            '90th_percentile': risk_df.quantile(0.90, axis=1),
            '99th_percentile': risk_df.quantile(0.99, axis=1)
        })
        # Format the risk DF with the appropriate strings
        risk_df = risk_df.apply(
            lambda row: pd.Series(
                [self._format_strings['Risk'].format(item) for item in row],
                index=row.index.values
            ),
            axis=1,
        )
        # Do not truncate our base64 images.
        detail_table = risk_df.to_html(
            border=0,
            header=True,
            justify='left',
            classes='fair_table',
            escape=False
        )
        return detail_table
