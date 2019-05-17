""""""

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options import Material

# Globals and constants variables.

@pytest.fixture
def materials():
    return [Material.pure(13),
            Material.from_formula('Al2O3'),
            Material('foo', {29: 0.5, 28: 0.5}, 2.0)]