#!/usr/bin/env python

# Standard library modules.
import os
import sys
from distutils.cmd import Command
from distutils import log, sysconfig, dir_util, archive_util
from distutils.command.build import show_compilers
import zipfile

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

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
        import requests_download
        import progressbar
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

with open(os.path.join(BASEDIR, 'README.rst'), 'r') as fp:
    LONG_DESCRIPTION = fp.read()

PACKAGES = find_packages()
PACKAGE_DATA = {}

INSTALL_REQUIRES = ['pymontecarlo', 'PyQt5', 'qtpy', 'matplotlib_scalebar',
                    'pyqttango', 'pygments', 'pandas']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage', 'progressbar2', 'requests_download']}

CMDCLASS = versioneer.get_cmdclass()
CMDCLASS['bdist_windows'] = bdist_windows

ENTRY_POINTS = {'gui_scripts':
                ['pymontecarlo = pymontecarlo_gui.__main__:main'],
                }

setup(name="pyMonteCarlo-GUI",
      version=versioneer.get_version(),
      url='https://github.com/pymontecarlo',
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

      packages=PACKAGES,
      package_data=PACKAGE_DATA,

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,

      test_suite='nose.collector',
)

