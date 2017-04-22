""""""

# Standard library modules.

# Third party modules.
from qtpy import QtGui, QtWebEngineWidgets

import dominate
import dominate.tags as tags

# Local modules.
from pymontecarlo_gui.widgets.field import Field
from pymontecarlo.formats.html.base import find_convert_htmlhandler

# Globals and constants variables.

class OptionsField(Field):

    CSS = """
h1 {
        font-size: 1.2em;
        margin: 10px 0;
    }
  
    h2 {
        font-size: 1.1em;
        color: #404040;
        margin: 10px 0 5px 0;
    }
  
    h3 {
        font-size: 1em;
        text-decoration: underline;
    }
  
    dl {
        margin: 0 0 0 1em;
    }
  
    dt {
        float: left;
        clear: left;
        text-align: left;
        font-variant: small-caps;
        padding-right: 2em;
    }
  
    table {
        border-collapse: collapse;
        border-spacing: 0;
        empty-cells: show;
        border: 1px solid #cbcbcb;
        border-bottom: 1px solid #cbcbcb;
    }

    td, th {
        border-left: 1px solid #cbcbcb;
        border-bottom: 1px solid #cbcbcb;
        border-width: 0 1px 0 1px;
        font-size: inherit;
        margin: 0;
        overflow: visible;
        padding: 0.4em 1em;
    }

    thead {
        background-color: #e0e0e0;
        color: #000;
        text-align: left;
        vertical-align: bottom;
    }
    
    tbody {
        text-align: left;
    }
"""

    def __init__(self, options):
        super().__init__()
        self._options = options
        self._widget = None

    def title(self):
        return 'Options'

    def icon(self):
        return QtGui.QIcon.fromTheme('document-properties')

    def widget(self):
        if self._widget is None:
            options = self.options()

            doc = dominate.document('Options')
            doc.head += tags.style(self.CSS)
            doc.body += find_convert_htmlhandler(options).convert(options).children
            html = doc.render()

            self._widget = QtWebEngineWidgets.QWebEngineView()
            self._widget.setHtml(html)
        return self._widget

    def options(self):
        return self._options
