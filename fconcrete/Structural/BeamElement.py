import numpy as np
from fconcrete.Structural.Node import Node, Nodes
from fconcrete.Structural.Section import unitary_section
from fconcrete.Structural.Material import unitary_material
import copy

class BeamElement:
    """
        Class that defines a primitive elements of a beam.
    """
    def __init__(self, nodes, section=unitary_section, material=unitary_material):
        """
            Define the beam_elements that, together, makes the whole Beam. 
            
                Call signatures:

                    fc.BeamElement(nodes, section=unitary_section, material=unitary_material)
            
            Parameters
            ----------
            nodes : list of Node
                list of fc.Node to represent the delimitation for the beam_element.

            section : Section, optional
                Define the section that are going to make the beam_element.
                Default fc.unitary_section.
                
            material : Material, optional
                Define a material and its properties.
                Default fc.unitary_material.
        """
        self.section = section
        self.material = material
        self.x = nodes
        self.E = material.E
        self.I = section.I
        self.n1 = nodes[0]
        self.n2 = nodes[1]
        self.length = nodes[1].x - nodes[0].x
        self.flexural_rigidity = material.E*section.I
        
    def get_matrix_rigidity_unitary(self):
        """
            Returns the unitary rigidity matrix. 
        """
        return self.flexural_rigidity/(self.length**3)*np.array([
                        [12, 6*self.length, -12, 6*self.length],
                        [6*self.length, 4*self.length**2, -6*self.length, 2*self.length**2],
                        [-12, -6*self.length, 12, -6*self.length],
                        [6*self.length, 2*self.length**2, -6*self.length, 4*self.length**2]
                    ])
    
    @classmethod
    def get_efforts_from_bar_element(cls, beam_element, load):
        """
            Get the efforts coused by the load in a double crimped beam element.
            
            Parameters
            ----------
            distance_a : number
                Distance, in cm, from the left node to the force.
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
        """
            Split a beam_element in two. The node in x is considered a Middle Node.
            
            Parameters
            ----------
            x : number
                Distance, in cm, from the left node to the split point.
        """
        if x >= self.n2.x or x <= self.n1.x: return [self]
        n_intermediate = Node.MiddleNode(x=x)
        bar1 = BeamElement(nodes=[self.n1, n_intermediate], section=self.section, material=self.material)
        bar2 = BeamElement(nodes=[n_intermediate, self.n2], section=self.section, material=self.material)
        return [bar1, bar2]
        
    def __repr__(self):
        return str(self.__dict__)


class BeamElements:
    """
        Class that defines a primitive elements of a beam list with easy to work properties and methods.
    """
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
        """
            Recommended way to create a BeamElements class.
        """
        if str(type(beam_elements)) == "<class 'fconcrete.Structural.BeamElement.BeamElements'>": return beam_elements
        beam_elements = np.array(beam_elements)
        x_start = np.array([ beam_element.n1.x for beam_element in beam_elements ])
        bar_sort_position = np.argsort(x_start)
        return cls(beam_elements[bar_sort_position])
    
    def split(self, x):
        """
            Similar to BeamElement.split, but can guess what element of the array is going to be splited.
        """
        new_beams = np.array([])
        for bar in self.bar_elements:
            new_beams = np.concatenate((new_beams, bar.split(x)))
        return BeamElements(new_beams)

    def changeProperty(self, prop, function, conditional=lambda x:True):
        """
            Change all properties of the beam elements in a single function.
        """
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
    