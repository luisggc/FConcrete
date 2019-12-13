"""Top-level package for FConcrete."""

__author__ = """Luis Gabriel Gonçalves Coimbra"""
__email__ = 'luiscoimbraeng@outlook.com'
__version__ = '0.1.0'
e = 0.00001
#np.set_printoptions(precision=3, suppress=True, linewidth=3000)

from fconcrete.helpers import *
from fconcrete.Structural import *
from fconcrete.ConcreteBeam import ConcreteBeam
from fconcrete.ConcreteSteels import ConcreteSteels
from fconcrete.Material import Material, Concrete