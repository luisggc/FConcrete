from fconcrete.Structural.Beam import Beam
from fconcrete.ConcreteSteels import ConcreteSteels

class ConcreteBeam(Beam):

    def __init__(self, loads, bars, steel=ConcreteSteels()):
        Beam.__init__(self, loads, bars, steel)