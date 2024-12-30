from setuptools import setup

setup(
    name="pyfair",
    version="0.1-alpha.13",
    description="Open FAIR Monte Carlo creator",
    long_description="""
        Factor Analysis of Information Risk (Open FAIR) model in Python.

        This package endeavors to create a simple API for automating the
        creation of FAIR Monte Carlo risk simulations.

        This is based on the terms found in:

        1. Open FAIR™ RISK TAXONOMY (O-RT); and,
        2. Open FAIR™ RISK ANALYSIS (O-RA).

        "Open FAIR" is a trademark of the Open Group.

    """,
    author="Hive Systems",
    author_email="pyfair@hivesystems.com",
    packages=[
        "pyfair",
        "pyfair.model",
        "pyfair.report",
        "pyfair.utility",
    ],
    license="MIT",
    url="https://github.com/Hive-Systems/pyfair",
    keywords=["FAIR", "risk", "monte carlo", "cyber risk", "risk analysis"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "xlrd",
    ],
    package_dir={"pyfair": "./pyfair"},
    package_data={"pyfair": ["./static/*"]},
    python_requires=">=3.6",
)
