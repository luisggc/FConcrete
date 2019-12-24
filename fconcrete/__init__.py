"""Top-level package for FConcrete."""

__author__ = """Luis Gabriel Gonçalves Coimbra"""
__email__ = 'luiscoimbraeng@outlook.com'
__version__ = '0.1.0'
from .AvailableMaterials import AvailableConcreteSteelBar
#np.set_printoptions(precision=3, suppress=True, linewidth=3000)
from .helpers import *
from .Structural import *
from .ConcreteBeam import ConcreteBeam
from .Material import Material, Concrete
    
def main():
    return


if __name__ == '__main__':
    
    main()