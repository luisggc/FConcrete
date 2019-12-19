"""Top-level package for FConcrete."""

__author__ = """Luis Gabriel Gonçalves Coimbra"""
__email__ = 'luiscoimbraeng@outlook.com'
__version__ = '0.1.0'
e = 0.00001

from pint import UnitRegistry
ureg = UnitRegistry()
ureg.define('kn_cm2 = kilonewton / centimeter ** 2 = kn_cm2')
ureg.define('kNcm = kilonewton * centimeter = kncm')
ureg.define('kNm = kilonewton * meter = knm')


_Q = ureg.Quantity

#np.set_printoptions(precision=3, suppress=True, linewidth=3000)

from fconcrete.helpers import *
from fconcrete.Structural import *
from fconcrete.ConcreteBeam import ConcreteBeam
from fconcrete.ConcreteSteels import ConcreteSteels
from fconcrete.Material import Material, Concrete


