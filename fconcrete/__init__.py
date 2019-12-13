import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=3000)
e = 0.00001

'''
from fconcrete.Structural.Beam import *
from fconcrete.Structural.Load import *
from fconcrete.Structural.Node import *
from fconcrete.Structural.Section import *
from fconcrete.Structural.SingleBeamElement import *
from fconcrete.Structural.Section import Section, Rectangle
'''

from fconcrete.helpers import *
from fconcrete.Structural import *
from fconcrete.ConcreteBeam import ConcreteBeam
from fconcrete.ConcreteSteels import ConcreteSteels
from fconcrete.Material import Material, Concrete