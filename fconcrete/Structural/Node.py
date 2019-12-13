import numpy as np

class Node:
    def __init__(self, x, condition_boundary):
        self.x = x
        self.condition_boundary = condition_boundary
        
    @classmethod
    def SimpleSupport(cls, x):
        return cls(x, [0, 1])
    
    @classmethod
    def Crimp(cls, x):
        return cls(x, [1, 1])
    
    @classmethod
    def MiddleNode(cls, x):
        return cls(x, [1, 1])
    
    def __repr__(self):
        return str(self.__dict__)


class Nodes:
    def __init__(self, nodes):
        self.nodes = np.array(nodes)
        self.x = np.array([ node.x for node in nodes ])
        self.condition_boundary = np.array([ node.condition_boundary for node in nodes ])
    
    def __repr__(self):
        return self.nodes
    
    def __getitem__(self, key):
        return self.nodes[key]
    
    def __len__(self):
        return len(self.nodes)
    