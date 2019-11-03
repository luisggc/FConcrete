import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=3000)
e = 0.00001

from fconcrete.helpers import *
from fconcrete.Load import Load, Loads
from fconcrete.Node import Node, Nodes
from fconcrete.SingleBeamElement import SingleBeamElement, SingleBeamElements
from fconcrete.Beam import Beam