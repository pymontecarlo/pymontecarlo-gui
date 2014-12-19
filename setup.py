#!/usr/bin/env python

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import codecs
import re

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
from pymontecarlo.util.dist.command.clean import clean
from pymontecarlo.util.dist.command.check import check

try:
    from cx_Freeze.dist import Distribution, build
    from cx_Freeze.freezer import Executable

    from pymontecarlo.util.dist.command.build_exe import build_exe
    from pymontecarlo.util.dist.command.bdist_exe import bdist_exe
    from pymontecarlo.util.dist.command.bdist_mac import bdist_mac
    from pymontecarlo.util.dist.command.bdist_dmg import bdist_dmg

    has_cx_freeze = True
except ImportError:
    has_cx_freeze = False

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

def find_version(*file_paths):
    """
    Read the version number from a source file.

    .. note::

       Why read it, and not import?
       see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
    """
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(BASEDIR, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

packages = find_packages(exclude=('pymontecarlo.util.dist*',))
namespace_packages = ['pymontecarlo',
                      'pymontecarlo.ui']
requirements = ['pyparsing', 'numpy', 'h5py', 'matplotlib', 'PySide',
                'pyxray', 'Pillow', 'latexcodec']

excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'tkinter', "wx", "scipy", "PyQt4",
            'ConfigParser', 'IPython', 'pygments', 'sphinx',
            'pyxray' # Because data files from pyxray are not copied in zip
            ]
includes = ['PIL' # Requires by some programs
            ]

build_exe_options = {"packages": packages,
                     "namespace_packages": namespace_packages,
                     "excludes": excludes,
                     "includes": includes,
                     "init_script": os.path.abspath('initscripts/Console.py'),
                     'include_msvcr': True}

gui_executables = {'pymontecarlo': 'pymontecarlo.ui.gui.main:run'}

entry_points = {'pymontecarlo.ui.gui.options.material':
                    ['Material = pymontecarlo.ui.gui.options.material:MaterialDialog'],
                'pymontecarlo.ui.gui.options.beam':
                    ['PencilBeam = pymontecarlo.ui.gui.options.beam:PencilBeamWidget',
                    'GaussianBeam = pymontecarlo.ui.gui.options.beam:GaussianBeamWidget', ],
                'pymontecarlo.ui.gui.options.geometry':
                    ['Substrate = pymontecarlo.ui.gui.options.geometry:SubstrateWidget',
                     'Inclusion = pymontecarlo.ui.gui.options.geometry:InclusionWidget',
                     'HorizontalLayers = pymontecarlo.ui.gui.options.geometry:HorizontalLayersWidget',
                     'VerticalLayers = pymontecarlo.ui.gui.options.geometry:VerticalLayersWidget',
                     'Sphere = pymontecarlo.ui.gui.options.geometry:SphereWidget'],
                'pymontecarlo.ui.gui.options.detector':
                    ['BackscatteredElectronEnergyDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronEnergyDetectorWidget',
                     'TransmittedElectronEnergyDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronEnergyDetectorWidget',
                     'BackscatteredElectronPolarAngularDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronPolarAngularDetectorWidget',
                     'TransmittedElectronPolarAngularDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronPolarAngularDetectorWidget',
                     'BackscatteredElectronAzimuthalAngularDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronAzimuthalAngularDetectorWidget',
                     'TransmittedElectronAzimuthalAngularDetector = pymontecarlo.ui.gui.options.detector:TransmittedElectronAzimuthalAngularDetectorWidget',
                     'BackscatteredElectronRadialDetector = pymontecarlo.ui.gui.options.detector:BackscatteredElectronRadialDetectorWidget',
                     'PhotonSpectrumDetector = pymontecarlo.ui.gui.options.detector:PhotonSpectrumDetectorWidget',
                     'PhotonDepthDetector = pymontecarlo.ui.gui.options.detector:PhotonDepthDetectorWidget',
                     'PhiZDetector = pymontecarlo.ui.gui.options.detector:PhiZDetectorWidget',
                     'PhotonRadialDetector = pymontecarlo.ui.gui.options.detector:PhotonRadialDetectorWidget',
                     'PhotonEmissionMapDetector = pymontecarlo.ui.gui.options.detector:PhotonEmissionMapDetectorWidget',
                     'PhotonIntensityDetector = pymontecarlo.ui.gui.options.detector:PhotonIntensityDetectorWidget',
                     'TimeDetector = pymontecarlo.ui.gui.options.detector:TimeDetectorWidget',
                     'ElectronFractionDetector = pymontecarlo.ui.gui.options.detector:ElectronFractionDetectorWidget',
                     'ShowersStatisticsDetector = pymontecarlo.ui.gui.options.detector:ShowersStatisticsDetectorWidget',
                     'TrajectoryDetector = pymontecarlo.ui.gui.options.detector:TrajectoryDetectorWidget', ],
                'pymontecarlo.ui.gui.options.limit':
                    ['TimeLimit = pymontecarlo.ui.gui.options.limit:TimeLimitWidget',
                     'ShowersLimit = pymontecarlo.ui.gui.options.limit:ShowersLimitWidget',
#                     'UncertaintyLimit = pymontecarlo.ui.gui.options.limit:UncertaintyLimitWidget '
                    ],
                'pymontecarlo.ui.gui.results.result':
                    [
                     'BackscatteredElectronEnergyResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronEnergyResultWidget',
                     'TransmittedElectronEnergyResult = pymontecarlo.ui.gui.results.result:TransmittedElectronEnergyResultWidget',
                     'BackscatteredElectronPolarAngularResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronPolarAngularResultWidget',
                     'TransmittedElectronPolarAngularResult = pymontecarlo.ui.gui.results.result:TransmittedElectronPolarAngularResultWidget',
                     'BackscatteredElectronAzimuthalAngularResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronAzimuthalAngularResultWidget',
                     'TransmittedElectronAzimuthalAngularResult = pymontecarlo.ui.gui.results.result:TransmittedElectronAzimuthalAngularResultWidget',
                     'BackscatteredElectronRadialResult = pymontecarlo.ui.gui.results.result:BackscatteredElectronRadialResultWidget',
                     'PhotonSpectrumResult = pymontecarlo.ui.gui.results.result:PhotonSpectrumResultWidget',
                     'PhotonDepthResult = pymontecarlo.ui.gui.results.result:PhotonDepthResultWidget',
                     'PhiZResult = pymontecarlo.ui.gui.results.result:PhiZResultWidget',
                     'PhotonRadialResult = pymontecarlo.ui.gui.results.result:PhotonRadialResultWidget',
#                     'PhotonEmissionMapResult = pymontecarlo.ui.gui.results.result:PhotonEmissionMapResultWidget',
                     'PhotonIntensityResult = pymontecarlo.ui.gui.results.result:PhotonIntensityResultWidget',
                     'TimeResult = pymontecarlo.ui.gui.results.result:TimeResultWidget',
                     'ElectronFractionResult = pymontecarlo.ui.gui.results.result:ElectronFractionResultWidget',
                     'ShowersStatisticsResult = pymontecarlo.ui.gui.results.result:ShowersStatisticsResultWidget',
                     'TrajectoryResult = pymontecarlo.ui.gui.results.result:TrajectoryResultWidget',
                     ]
                }

entry_points['gui_scripts'] = \
    ['%s = %s' % item for item in gui_executables.items()]

executables = []
distclass = None
cmdclass = {'clean': clean, "check": check}
options = {}

if has_cx_freeze:
    def _make_executable(target_name, script, gui=False):
        path = os.path.join(*script.split(":")[0].split('.')) + '.py'
        if sys.platform == "win32": target_name += '.exe'
        base = "Win32GUI" if sys.platform == "win32" and gui else None
        return Executable(path, targetName=target_name, base=base,
                          shortcutName=target_name)

    executables = []
    for target_name, script in gui_executables.items():
        executables.append(_make_executable(target_name, script, True))

    distclass = Distribution
    cmdclass.update({"build": build,
                     "build_exe": build_exe, "bdist_exe": bdist_exe,
                     "bdist_mac": bdist_mac, "bdist_dmg": bdist_dmg})
    options.update({"build_exe": build_exe_options})

setup(name="pyMonteCarlo-GUI",
      version=find_version('pymontecarlo', 'ui', 'gui', 'main.py'),
      url='http://pymontecarlo.bitbucket.org',
      description="Python interface for Monte Carlo simulation programs",
      author="Hendrix Demers and Philippe T. Pinard",
      author_email="hendrix.demers@mail.mcgill.ca and philippe.pinard@gmail.com",
      license="GPL v3",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=packages,
      namespace_packages=namespace_packages,

      distclass=distclass,
      cmdclass=cmdclass,

      setup_requires=['nose'],
      install_requires=requirements,

      entry_points=entry_points,
      executables=executables,

      options=options,

      test_suite='nose.collector',
)

