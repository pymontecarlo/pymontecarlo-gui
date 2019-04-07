""""""

# Standard library modules.
import os
import sys
import argparse
import platform
import asyncio
import logging
import ctypes
import threading
logger = logging.getLogger(__name__)

# Third party modules.
from qtpy import QtCore, QtWidgets

#from asyncqt import QEventLoop

import matplotlib
matplotlib.use('qt5agg')

# Local modules.
import pymontecarlo
from pymontecarlo.entity import EntityBase
from pymontecarlo.util.path import get_config_dir
from pymontecarlo.util.process import kill_process

import pymontecarlo_gui
import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.main import MainWindow
from pymontecarlo_gui.widgets.icon import load_pixmap
from pymontecarlo_gui.options.program.base import ProgramFieldBase

# Globals and constants variables.

def _create_parser():
    usage = 'pymontecarlo'
    description = 'Open pymontecarlo graphical user interface.'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in debug mode')

    return parser

def _setup(ns):
    # Configuration directory
    configdir = get_config_dir()
    frozen = getattr(sys, 'frozen', False)

    # Redirect stdout and stderr when frozen
    if frozen:
        filepath = os.path.join(configdir, 'pymontecarlo.stdout')
        sys.stdout = open(filepath, 'w')

        # NOTE: Important since warnings required sys.stderr not be None
        filepath = os.path.join(configdir, 'pymontecarlo.stderr')
        sys.stderr = open(filepath, 'w')

    # Logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if ns.verbose else logging.INFO)

    fmt = '%(asctime)s - %(levelname)s - %(module)s - %(lineno)d: %(message)s'
    formatter = logging.Formatter(fmt)

    handler = logging.FileHandler(os.path.join(configdir, 'pymontecarlo.log'), 'w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not frozen:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info('Started pyMonteCarlo')
    logger.info('pymontecarlo version = %s', pymontecarlo.__version__)
    logger.info('pymontecarlo-gui version = %s', pymontecarlo_gui.__version__)
    logger.info('operating system = %s %s', platform.system(), platform.release())
    logger.info('machine = %s', platform.machine())
    logger.info('processor = %s', platform.processor())

    # Log plugins
    for name in sorted(pymontecarlo.pymontecarlo_plugins):
        logger.info('Found plug-in: {}'.format(name))

    # Log entities
    entities = []
    for clasz in EntityBase._subclasses:
        entities.append('{}.{}'.format(clasz.__module__, clasz.__name__))

    for clasz in ProgramFieldBase._subclasses:
        entities.append('{}.{}'.format(clasz.__module__, clasz.__name__))

    for entity in sorted(entities):
        logger.info('Registered entity: {}'.format(entity))

    # Catch all exceptions
    def _excepthook(exc_type, exc_obj, exc_tb):
        sys.__excepthook__(exc_type, exc_obj, exc_tb)
        messagebox.exception(None, exc_obj)
    sys.excepthook = _excepthook

    # Output sys.path
    logger.info("sys.path = %s", sys.path)

    # Output environment variables
    logger.info('ENVIRON = %s' % os.environ)

    # Change app id on Windows
    # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
    if sys.platform == 'win32':
        myappid = 'com.github.pymontecarlo.main' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def _find_programs():
    return tuple(ProgramFieldBase._subclasses)

def run_app(loop):
    # According to
    # https://stackoverflow.com/questions/37693818/run-pyqt-gui-main-app-in-seperate-thread
    asyncio.set_event_loop(loop)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')

    pixmap = load_pixmap('splash.svg')
    message = 'Version: {}'.format(pymontecarlo_gui.__version__)
    splash_screen = QtWidgets.QSplashScreen(pixmap)
    splash_screen.showMessage(message, QtCore.Qt.AlignRight)
    splash_screen.show()
    app.processEvents()

    window = MainWindow(loop)
    window.show()

    splash_screen.finish(window)

    app.exec_()

    loop.stop()
    logger.debug('UI thread finished')

    # Self kill
    kill_process(os.getpid())

def _parse(ns):
    # Change event loop for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # asyncio.get_child_watcher()
    loop.set_debug(True)
    logger.debug('New event loop id={}'.format(id(loop)))

    # Create UI thread
    thread = threading.Thread(target=run_app, args=(loop,))
    thread.start()

    loop.run_forever()

def main():
    parser = _create_parser()

    ns = parser.parse_args()
    _setup(ns)
    _parse(ns)

if __name__ == '__main__':
    main()
