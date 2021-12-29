#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, "README.rst"), "r") as fp:
    LONG_DESCRIPTION = fp.read()

PACKAGES = find_packages()
PACKAGE_DATA = {"pymontecarlo_gui": ["icons/*.svg", "icons/*.png"]}

with open(os.path.join(BASEDIR, "requirements.txt"), "r") as fp:
    INSTALL_REQUIRES = fp.read().splitlines()

EXTRAS_REQUIRE = {}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {
    "gui_scripts": ["pymontecarlo = pymontecarlo_gui.__main__:main"],
}

setup(
    name="pyMonteCarlo-GUI",
    version=versioneer.get_version(),
    url="https://github.com/pymontecarlo",
    description="Python interface for Monte Carlo simulation programs",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Hendrix Demers and Philippe T. Pinard",
    author_email="hendrix.demers@mail.mcgill.ca and philippe.pinard@gmail.com",
    license="GPL v3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    cmdclass=CMDCLASS,
    entry_points=ENTRY_POINTS,
    test_suite="nose.collector",
)
