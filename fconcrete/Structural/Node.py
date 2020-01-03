import numpy as np
from fconcrete.helpers import to_unit

class Node:
    def __init__(self, x, condition_boundary, length=0):
        x = to_unit(x, "cm").magnitude
        self.x = x
        self.condition_boundary = condition_boundary
        self.length = length
        
    @classmethod
    def SimpleSupport(cls, x, length=0):
        return cls(x, [0, 1], length)
    
    @classmethod
    def Free(cls, x):
        return cls(x, [1, 1])
    
    @classmethod
    def MiddleNode(cls, x):
        return cls(x, [1, 1])
    
    @classmethod
    def Crimp(cls, x, length=0):
        return cls(x, [0, 0], length)
    
    def __repr__(self):
        return str(self.__dict__)+'\n'


class Nodes:
    def __init__(self, nodes):
        self.nodes = np.array(nodes)
        self.x = np.array([ node.x for node in nodes ])
        self.condition_boundary = np.array([ node.condition_boundary for node in nodes ])
    
    def __repr__(self):
        return str(self.nodes)
    
    def __getitem__(self, key):
        return self.nodes[key]
    
    def __len__(self):
        return len(self.nodes)
    