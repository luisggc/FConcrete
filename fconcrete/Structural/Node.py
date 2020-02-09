import numpy as np
from fconcrete.helpers import to_unit

class Node:
    def __init__(self, x, condition_boundary, length=0):
        """
            Represents a generical node.
            Node is the delimitation for a beam_element.
        """
        x = to_unit(x, "cm")
        length = to_unit(length, "cm")
        self.x = x
        self.condition_boundary = condition_boundary
        self.length = length
        
    @classmethod
    def SimpleSupport(cls, x, length=0):
        """
            Represents a node with vertical displacement equal to zero.
            But it allows rotation.
            
            Call signatures:

                    fc.Node.SimpleSupport(x, length=0)

                >>> simple_support_1 = fc.Node.SimpleSupport(100)
                >>> simple_support_2 = fc.Node.SimpleSupport('1m')
                >>> repr(simple_support_1) == repr(simple_support_2)
                True

            Parameters
            ----------
            x : number or str
                Position of the node. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc
            
            length : number or str, optional
                Length of the node if applicable. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc.
                Default is 0.
        """
        return cls(x, [0, 1], length)
    
    @classmethod
    def Free(cls, x):
        """
            Represents a node with vertical displacement and rotation.
            
            Call signatures:

                    fc.Node.Free(x)

                >>> free_node_1 = fc.Node.Free(100)
                >>> free_node_2 = fc.Node.Free('1m')
                >>> repr(free_node_1) == repr(free_node_2)
                True
            
            Parameters
            ----------
            x : number or str
                Position of the node. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc
        """
        return cls(x, [1, 1])
    
    @classmethod
    def MiddleNode(cls, x):
        """
            Represents a node with vertical displacement and rotation.
            
            Call signatures:

                    fc.Node.Free(x)

                >>> middle_node_1 = fc.Node.MiddleNode(100)
                >>> middle_node_2 = fc.Node.MiddleNode('1m')
                >>> repr(middle_node_1) == repr(middle_node_2)
                True
            
            Parameters
            ----------
            x : number or str
                Position of the node. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc
        """
        return cls(x, [1, 1])
    
    @classmethod
    def Crimp(cls, x, length=0):
        """
            Represents a node with vertical displacement and rotation equal to zero.
            
            Call signatures:

                    fc.Node.Crimp(x)

                >>> crimp_node_1 = fc.Node.Crimp(100)
                >>> crimp_node_2 = fc.Node.Crimp('1m')
                >>> repr(crimp_node_1) == repr(crimp_node_2)
                True
            
            Parameters
            ----------
            x : number or str
                Position of the node. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc
            
            length : number or str, optional
                Length of the node if applicable. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20m', '10dm', etc.
                Default is 0.
        """
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
    