""""""

# Standard library modules.
import os
import sys
import argparse
import logging
import platform

# Third party modules.
from qtpy import QtWidgets

# Local modules.
import pymontecarlo
from pymontecarlo.util.path import get_config_dir

import pymontecarlo_gui
import pymontecarlo_gui.widgets.messagebox as messagebox
from pymontecarlo_gui.settings import SettingsMainWindow
from pymontecarlo_gui.main import MainWindow

# Globals and constants variables.

def _create_parser():
    usage = 'pymontecarlo'
    description = 'Open pymontecarlo graphical user interface.'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('-c', '--config', action='store_true',
                        help='Open only settings dialog')

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

#    if not frozen:
#        handler = logging.StreamHandler()
#        handler.setFormatter(formatter)
#        logger.addHandler(handler)

    logger.info('Started pyMonteCarlo')
    logger.info('pymontecarlo version = %s', pymontecarlo.__version__)
    logger.info('pymontecarlo-gui version = %s', pymontecarlo_gui.__version__)
    logger.info('operating system = %s %s', platform.system(), platform.release())
    logger.info('machine = %s', platform.machine())
    logger.info('processor = %s', platform.processor())

    # Catch all exceptions
#    def _excepthook(exc_type, exc_obj, exc_tb):
#        messagebox.exception(None, exc_obj)
#        sys.__excepthook__(exc_type, exc_obj, exc_tb)
#    sys.excepthook = _excepthook

    # Output sys.path
    logger.info("sys.path = %s", sys.path)

    # Output environment variables
    logger.info('ENVIRON = %s' % os.environ)

def _parse(ns):
    app = QtWidgets.QApplication(sys.argv)

    if ns.config:
        window = SettingsMainWindow()
        window.setSettings(pymontecarlo.settings)
        window.show()
    else:
        window = MainWindow()
        window.show()

        window.openProject('/tmp/example.mcsim')

    app.exec_()

def main():
    parser = _create_parser()

    ns = parser.parse_args()
    _setup(ns)
    _parse(ns)

if __name__ == '__main__':
    main()
