"""Script to create and run a test suite."""

import pathlib
import sys
import unittest

# Add pyfair directory to path
this_file = pathlib.Path(__file__).absolute()
repo_dir = this_file.parents[1]
path = str(repo_dir)
sys.path.append(path)

# Import test modules
import model.test_base
import model.test_meta_model
import model.test_model
import model.test_model_calc
import model.test_model_input
import model.test_model_node
import model.test_model_tree
import report.test_base_curve
import report.test_base_report
import report.test_distribution
import report.test_exceedence
import report.test_simple_report
import report.test_tree_graph
import report.test_violin
import utility.test_beta_pert
import utility.test_database
import utility.test_factory
import utility.test_fair_exception

# List test modules
test_modules = [
    # Model Module
    model.test_meta_model,
    model.test_model_calc,
    model.test_model_input,
    model.test_model_node,
    model.test_model_tree,
    model.test_model,
    model.test_base,
    # Report Module
    report.test_base_curve,
    report.test_base_report,
    report.test_distribution,
    report.test_exceedence,
    report.test_simple_report,
    report.test_tree_graph,
    report.test_violin,
    # Utility Module
    utility.test_beta_pert,
    utility.test_database,
    utility.test_factory,
    utility.test_fair_exception,
]

if __name__ == "__main__":
    # Create loader and suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add to suite
    for test_module in test_modules:
        loaded_test = loader.loadTestsFromModule(test_module)
        suite.addTest(loaded_test)

    # Create runner and run
    runner = unittest.TextTestRunner(verbosity=5)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
