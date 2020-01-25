import numpy as np
from fconcrete.Structural.Node import Node, Nodes
from fconcrete.Structural.Section import unitary_section
from fconcrete.Structural.Material import unitary_material
import copy

class BeamElement:
    def __init__(self, nodes, section=unitary_section, material=unitary_material): #, function_d=lambda height,c: height-c ):
        self.section = section
        #section.d = function_d(section.height, material.c) if hasattr(material,"c") else 0
        self.material = material
        self.x = nodes
        self.E = material.E
        self.I = section.I
        self.n1 = nodes[0]
        self.n2 = nodes[1]
        self.length = nodes[1].x - nodes[0].x
        self.flexural_rigidity = material.E*section.I
        
    def get_matrix_rigidity_unitary(self):
        return self.flexural_rigidity/(self.length**3)*np.array([
                        [12, 6*self.length, -12, 6*self.length],
                        [6*self.length, 4*self.length**2, -6*self.length, 2*self.length**2],
                        [-12, -6*self.length, 12, -6*self.length],
                        [6*self.length, 2*self.length**2, -6*self.length, 4*self.length**2]
                    ])
    
    @classmethod
    def get_efforts_from_bar_element(cls, beam_element, load):
        """
        distance_a means the force_distance_from_nearest_left_node
        condition represent the degrees of freedom of the node. 1 means fixed and 0 free.
        """
        force = load.force
        length = beam_element.length
        order = load.order    
        distance_a = load.x - beam_element.x[0].x
                
        if distance_a>length: raise Exception("Distance from node cannot exceed the beam size.")
        distance_b = length - distance_a

        if order == 0:
            ma= force*distance_a*distance_b**2/length**2
            mb= -force*distance_b*distance_a**2/length**2 
            ra = (force*distance_b+ma+mb)/length
        elif order == 1:
            ma= load.q*length**2/12
            mb= -ma
            ra = load.q*length/2
        
        return -np.array([ra, ma, force-ra, mb])
 
    def split(self, x):
        if x >= self.n2.x or x <= self.n1.x: return [self]
        n_intermediate = Node.MiddleNode(x=x)
        bar1 = BeamElement(nodes=[self.n1, n_intermediate], section=self.section, material=self.material)
        bar2 = BeamElement(nodes=[n_intermediate, self.n2], section=self.section, material=self.material)
        return [bar1, bar2]
        
    def __repr__(self):
        return str(self.__dict__)


class BeamElements:
    def __init__(self, bar_elements):
        self.bar_elements = np.array(bar_elements)
        self.materials = np.array([ bar_element.material for bar_element in bar_elements ])
        self.sections = np.array([ bar_element.section for bar_element in bar_elements ])
        self.x_start = np.array([ bar_element.n1.x for bar_element in bar_elements ])
        self.x_end = np.array([ bar_element.n2.x for bar_element in bar_elements ])
        self.length = np.array([ bar_element.length for bar_element in bar_elements ])
        self.flexural_rigidity = np.array([ bar_element.flexural_rigidity for bar_element in bar_elements ])
        self.nodes = Nodes(np.concatenate((
                [ beam.n1 for beam in bar_elements ],
                [bar_elements[-1].n2 ] 
        )))
        condition_boundary = np.vstack((
            [ beam.n1.condition_boundary for beam in bar_elements ],
            bar_elements[-1].n2.condition_boundary
        ))
        self.condition_boundary = (condition_boundary.reshape((1, condition_boundary.size))==1)[0]
    
    @classmethod
    def create(cls, beam_elements):
        if str(type(beam_elements)) == "<class 'fconcrete.Structural.BeamElement.BeamElements'>": return beam_elements
        
        beam_elements = np.array(beam_elements)
        x_start = np.array([ beam_element.n1.x for beam_element in beam_elements ])
        bar_sort_position = np.argsort(x_start)
        return cls(beam_elements[bar_sort_position])
    
    def split(self, x):
        new_beams = np.array([])
        for bar in self.bar_elements:
            new_beams = np.concatenate((new_beams, bar.split(x)))
        return BeamElements(new_beams)

    def changeProperty(self, prop, function, conditional=lambda x:True):
            beam_elements = copy.deepcopy(self)
            for previous_beam_element in beam_elements:
                if conditional(previous_beam_element):
                    current_attribute_value = getattr(previous_beam_element, prop)
                    setattr(previous_beam_element, prop, function(current_attribute_value)) 
            return BeamElements(beam_elements.bar_elements)

    def __repr__(self):
        return str(self.__dict__)    
    
    def __getitem__(self, key):
        return self.bar_elements[key]
    
    def __len__(self):
        return len(self.bar_elements)
    