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
from distutils.cmd import Command
from distutils import log, sysconfig, dir_util, archive_util
from distutils.command.build import show_compilers
import zipfile

# Third party modules.
from setuptools import setup, find_packages
import requests_download
import progressbar

# Local modules.
from pymontecarlo.util.dist.command.clean import clean
from pymontecarlo.util.dist.command.check import check

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

class bdist_windows(Command):

    PYTHON_EMBED_URL = 'https://www.python.org/ftp/python/3.5.2/python-3.5.2-embed-amd64.zip'
    GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'
    PY_MAIN_EXE = """
#include <windows.h>
#include <stdio.h>
#include "Python.h"

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPWSTR lpstrCmd, int nShow)
{{
    wchar_t *argc[] = {{ L"-I", L"-c", L"import {module}; {module}.{method}()" }};
    return Py_Main(3, argc);
}}
    """

    EXE_MANIFEST = """

<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo>
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1"> 
    <application> 
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/> 
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application> 
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls"
                        version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*" />
    </dependentAssembly>
  </dependency>
</assembly>
    """

    description = "Build windows executable"

    user_options = [
        ('icon=', None, 'filename of icon to use'),
        ('dist-dir=', 'd',
         "directory to put final built distributions in "
         "[default: dist]"),
        ('compiler=', 'c', "specify the compiler type"),
        ('wheel-dir=', None, 'directory containing wheels already downloaded'),
        ('zip', None, 'create zip of the program at the end'),
        ('no-clean', None, 'do not remove the existing distribution'),
    ]

    boolean_options = ['zip', 'no-clean']

    help_options = [
        ('help-compiler', None,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.icon = None
        self.dist_dir = None
        self.compiler = None
        self.wheel_dir = None
        self.zip = False
        self.no_clean = False

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def download_file(self, url, filepath):
        progress = progressbar.DataTransferBar()
        trackers = [requests_download.ProgressTracker(progress)]
        requests_download.download(url, filepath, trackers=trackers)

    def download_python_embedded(self, workdir):
        filepath = os.path.join(workdir, 'python_embed.zip')

        try:
            log.info('downloading {0}'.format(self.PYTHON_EMBED_URL))
            self.download_file(self.PYTHON_EMBED_URL, filepath)

            log.info('extracting zip in {0}'.format(workdir))
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.extractall(workdir)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def install_pip(self, pythonexe):
        filepath = os.path.join(os.path.dirname(pythonexe), 'get-pip.py')

        try:
            log.info('downloading {0}'.format(self.GET_PIP_URL))
            self.download_file(self.GET_PIP_URL, filepath)

            self.spawn([pythonexe, filepath], search_path=False)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def install_distribution(self, pythonexe):
        cmd = [pythonexe, '-m', 'pip', 'install', '-U']
        if self.wheel_dir:
            cmd += ['--find-links', self.wheel_dir]

        for command, _version, filepath in self.distribution.dist_files:
            if command != 'bdist_wheel':
                continue
            cmd.append(filepath)

        self.spawn(cmd, search_path=False)

    def create_pymain_exe(self, workdir, name, cmd):
        from distutils.ccompiler import new_compiler

        c_filepath = os.path.join(workdir, name + '.c')
        manifest_filepath = os.path.join(workdir, name + '.exe.manifest')

        # Create code
        with open(c_filepath, 'w') as fp:
            fp.write(cmd)

        # Create manifest
        with open(manifest_filepath, 'w') as fp:
            fp.write(self.EXE_MANIFEST)

        # Compile
        objects = []
        try:
            compiler = new_compiler(compiler=self.compiler,
                                    verbose=self.verbose,
                                    dry_run=self.dry_run,
                                    force=self.force)
            compiler.initialize()

            py_include = sysconfig.get_python_inc()
            plat_py_include = sysconfig.get_python_inc(plat_specific=1)
            compiler.include_dirs.append(py_include)
            if plat_py_include != py_include:
                compiler.include_dirs.append(plat_py_include)

            compiler.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))

            objects = compiler.compile([c_filepath])
            output_progname = os.path.join(workdir, name)
            compiler.link_executable(objects, output_progname)
        finally:
            if os.path.exists(c_filepath):
                os.remove(c_filepath)
            if os.path.exists(manifest_filepath):
                os.remove(manifest_filepath)
            for filepath in objects:
                os.remove(filepath)

    def run(self):
        # Build wheel
        log.info('preparing a wheel file of application')
        self.run_command('bdist_wheel')

        # Create working directory
        fullname = '{0}-{1}'.format(self.distribution.get_name(),
                                    self.distribution.get_version())
        workdir = os.path.join(self.dist_dir, fullname)
        if os.path.exists(workdir) and not self.no_clean:
            dir_util.remove_tree(workdir)
        self.mkpath(workdir)

        # Install python
        pythonexe = os.path.join(workdir, 'python.exe')
        if not os.path.exists(pythonexe):
            self.download_python_embedded(workdir)

        # Install pip
        self.install_pip(pythonexe)

        # Install project
        self.install_distribution(pythonexe)

        # Process entry points
        for entry_point in self.distribution.entry_points['gui_scripts']:
            name, value = entry_point.split('=')
            module, method = value.split(':')

            name = name.strip()
            module = module.strip()
            method = method.strip()

            cmd = self.PY_MAIN_EXE.format(module=module, method=method)
            self.create_pymain_exe(workdir, name, cmd)

        # Create zip
        if self.zip:
            zipfilepath = os.path.join(self.dist_dir, fullname)
            archive_util.make_zipfile(zipfilepath, workdir)

packages = find_packages(exclude=('pymontecarlo.util.dist*',))
namespace_packages = ['pymontecarlo',
                      'pymontecarlo.ui']
requirements = ['pyparsing',
                'numpy==1.11.2+mkl',
                'h5py==2.6.0',
                'matplotlib==1.5.3',
                'PyQt5==5.7.1',
                'pyxray==0.1',
                'Pillow==3.4.2',
                'latexcodec',
                'qtpy',
                'pymontecarlo',
                'pymontecarlo-winxray==0.1.0']

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
cmdclass = {'clean': clean, "check": check, 'bdist_windows': bdist_windows}
options = {}

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

      setup_requires=['nose', 'requests', 'requests-download', 'progressbar2'],
      install_requires=requirements,

      entry_points=entry_points,
      executables=executables,

      options=options,

      test_suite='nose.collector',
)
