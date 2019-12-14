import numpy as np
from fconcrete.Structural.Node import Node

class SingleBeamElement:
    def __init__(self, nodes, section, max_types_of_bars=1):
        self.section = section
        self.material = section.material
        self.x = nodes
        self.E = section.material.E
        self.I = section.I
        self.max_types_of_bars = max_types_of_bars
        self.n1 = nodes[0]
        self.n2 = nodes[1]
        self.length = nodes[1].x - nodes[0].x
        self.flexural_rigidity = section.material.E*section.I
        
    def get_matrix_rigidity_unitary(self):
        #waring(ajeitar unidade)
        return self.flexural_rigidity/(self.length**3)*np.array([
                        [12, 6*self.length, -12, 6*self.length],
                        [6*self.length, 4*self.length**2, -6*self.length, 2*self.length**2],
                        [-12, -6*self.length, 12, -6*self.length],
                        [6*self.length, 2*self.length**2, -6*self.length, 4*self.length**2]
                    ])
    
    @classmethod
    def get_efforts_from_bar_element(cls, force, distance_a, length):
        """
        distance_a means the force_distance_from_nearest_left_node
        condition represent the degrees of freedom of the node. 1 means fixed and 0 free.
        """
        if distance_a>length: raise Exception("Distance from node cannot exceed the beam size.")
        distance_b = length - distance_a

        ma= force*distance_a*distance_b**2/length**2
        mb= -force*distance_b*distance_a**2/length**2 
        ra = (force*distance_b+ma+mb)/length   
        return -np.array([ra, ma, force-ra, mb])
 
    def split(self, x):
        if x >= self.n2.x or x <= self.n1.x: return [self]
        n_intermediate = Node.MiddleNode(x=x)
        bar1 = SingleBeamElement(nodes=[self.n1, n_intermediate], section=self.section)
        bar2 = SingleBeamElement(nodes=[n_intermediate, self.n2], section=self.section)
        return [bar1, bar2]
        
    def __repr__(self):
        return str(self.__dict__)


class SingleBeamElements:
    def __init__(self, bar_elements):
        self.bar_elements = np.array(bar_elements)
        self.x_start = np.array([ bar_element.n1.x for bar_element in bar_elements ])
        self.x_end = np.array([ bar_element.n2.x for bar_element in bar_elements ])
        self.length = np.array([ bar_element.length for bar_element in bar_elements ])
        self.flexural_rigidity = np.array([ bar_element.flexural_rigidity for bar_element in bar_elements ])
        self.nodes = np.concatenate((
                [ beam.n1 for beam in bar_elements ],
                [bar_elements[-1].n2 ] 
        ))
        condition_boundary = np.vstack((
            [ beam.n1.condition_boundary for beam in bar_elements ],
            bar_elements[-1].n2.condition_boundary
        ))
        self.condition_boundary = (condition_boundary.reshape((1, condition_boundary.size))==1)[0]
    
    @classmethod
    def create(cls, bar_elements):
        bar_elements = np.array(bar_elements)
        x_start = np.array([ bar_element.n1.x for bar_element in bar_elements ])
        bar_sort_position = np.argsort(x_start)
        return cls(bar_elements[bar_sort_position])
    
    def split(self, x):
        new_beams = np.array([])
        for bar in self.bar_elements:
            new_beams = np.concatenate((new_beams, bar.split(x)))
        return SingleBeamElements(new_beams)

    def __repr__(self):
        return str(self.__dict__)    
    
    def __getitem__(self, key):
        return self.bar_elements[key]
    
    def __len__(self):
        return len(self.bar_elements)
    