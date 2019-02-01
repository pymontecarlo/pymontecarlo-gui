""""""

# Standard library modules.
import asyncio
import logging
logger = logging.getLogger(__name__)

# Third party modules.
from qtpy import QtCore

# Local modules.

# Globals and constants variables.

class ExecutionThread(QtCore.QThread):

    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def run(self):
        logger.debug('Start of execution thread')

        asyncio.set_event_loop(self.loop)

        self.loop.run_forever()

        logger.debug('End of execution thread')
