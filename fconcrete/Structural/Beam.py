from fconcrete.Structural.BeamElement import BeamElement, BeamElements
from fconcrete.Structural.Load import Load, Loads
from fconcrete.Structural.Node import Nodes
from fconcrete.helpers import cond
from fconcrete.config import e
import copy
import numpy as np
import warnings
import matplotlib.pyplot as plt

class Beam:

    def __init__(self, loads, beam_elements, **options):
        beam_elements = BeamElements.create(beam_elements)
        external_loads = Loads.create(loads)
        self.initial_beam_elements = beam_elements
        beam_elements = self.createIntermediateBeams(external_loads, beam_elements)
        self.x_begin, self.x_end = beam_elements.nodes[0].x, beam_elements.nodes[-1].x
        
        self.external_loads = external_loads
        self.beam_elements = beam_elements
        
        self.length = sum(beam_elements.length)
        self.beams_quantity = len(beam_elements)
        
        if options.get("solve_structural") != False:
            self.solve_structural()
            if options.get("solve_displacement") != False:
                self.solve_displacement_constants()
        
    def solve_structural(self):
        nodal_efforts = self.getSupportReactions()
        self.nodal_efforts = nodal_efforts
        nodes = Nodes(self.beam_elements.nodes)
        self.nodes = nodes
        loads = self.external_loads
        for index, node in enumerate(nodes.nodes):
            loads = loads.add(
                [Load(nodal_efforts[index*2], nodal_efforts[index*2+1], node.x, node.x)]
                )
        self.loads = loads
                   
    @staticmethod
    def createIntermediateBeams(loads, bars):
        for load in loads.loads:
            bars = bars.split(load.x_begin)
            bars = bars.split(load.x_end)
        
        return bars

    def matrix_rigidity_global(self):
        matrix_rigidity_row = 2*self.beams_quantity+2
        matrix_rigidity_global = np.zeros(
            (matrix_rigidity_row, matrix_rigidity_row))
        for beam_n, beam in enumerate(self.beam_elements):
            matrix_rigidity_global[beam_n*2:beam_n*2+4,
                                   beam_n*2:beam_n*2+4] += beam.get_matrix_rigidity_unitary()
        return matrix_rigidity_global

    def get_beams_efforts(self):
        beams_efforts = np.zeros(self.beams_quantity*4)

        for load in self.external_loads.loads:
            if (load.x == self.x_end):
                load.x = self.x_end - e
            force_beam, beam_element = self.getBeamElementInX(load.x)

            beams_efforts[4*force_beam:4*force_beam+4] += BeamElement.get_efforts_from_bar_element(
                beam_element,
                load
            )

        # juntar vigas separadas em um vetor por nó
        bn = self.beams_quantity
        b = 2*np.arange(0, 2*bn+2, 1)
        b[1::2] = b[0::2]+1
        b[1] = b[-1] = b[-2] = 0
        mult_b = b != 0

        a = 2*(np.arange(0, 2*bn+2, 1)-1)
        a[0] = 0
        a[1::2] = a[0::2]+1

        return beams_efforts[a] + beams_efforts[b]*mult_b

    def getSupportReactions(self):
        condition_boundary = self.beam_elements.condition_boundary
        beams_efforts = self.get_beams_efforts()
        matrix_rigidity_global = self.matrix_rigidity_global()

        matrix_rigidity_global_determinable = matrix_rigidity_global[condition_boundary, :][:, condition_boundary]
        beams_efforts_determinable = beams_efforts[condition_boundary]

        U = np.zeros(len(condition_boundary))
        U[condition_boundary] = np.linalg.solve(matrix_rigidity_global_determinable, beams_efforts_determinable)
        self.U = U
        F = matrix_rigidity_global @ U

        return beams_efforts - F
    

    def getBeamElementInX(self, x):
            index = 0 if x<=self.x_begin else -1 if x>=self.x_end else np.where(
            np.array([node.x for node in self.beam_elements.nodes]) <= x)[0][-1]
            bar_element = self.beam_elements[index]
            return index, bar_element
        
    def getInternalShearStrength(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end:
                return 0
            f_value = 0
            for load in self.loads.loads:
                f_value += load.force * \
                    cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
                f_value += load.q*cond(x-load.x_begin, order=load.order) - load.q*cond(
                    x-load.x_end, order=load.order) if load.x_begin != load.x_end else 0
            return f_value
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getInternalShearStrength(x_element) for x_element in x ])
        
    def getShearDiagram(self, **options):
        return self._createDiagram(self.getInternalShearStrength, **options)

    def getInternalMomentumStrength(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end:
                return 0
            f_value = 0
            for load in self.loads.loads:
                f_value += -load.momentum * \
                    cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
                f_value += load.force * \
                    cond(x-load.x_begin, order=1) if load.order == 0 else 0
                f_value += (load.q*cond(x-load.x_begin, order=load.order+1) -
                            load.q*cond(x-load.x_end, order=load.order+1))/(load.order+1)
            return f_value
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getInternalMomentumStrength(x_element) for x_element in x ])
        
    def getMomentumDiagram(self, **options):
        return self._createDiagram(self.getInternalMomentumStrength, **options)
    
    def solve_displacement_constants(self):
        nodes = self.initial_beam_elements.nodes
        null_displacement = nodes.x[nodes.condition_boundary[:, 0]==0]
        null_rotation = nodes.x[nodes.condition_boundary[:, 1]==0]
        
        x1 = null_displacement[0]
        rest1 = self.getDisplacement(x1)
        
        if len(null_displacement)>=2:
            x2 = null_displacement[-1]
            rest2 = self.getDisplacement(x2)
            c1 = -(rest1 - rest2)/(x1-x2)
            c2 = -rest1 - c1*x1
        elif len(null_rotation)>=1 and len(null_displacement)>=1:
            x2 = null_rotation[0]
            c1 = -self.getRotation(x2)

        c2 = -rest1 - c1*x1
        
        self._c1 = c1
        self._c2 = c2
            
    
    
    
    def getDisplacementDiagram(self, **options):
        return self._createDiagram(self.getDisplacement, **options)
    
    def getRotation(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end: return 0
            f_value = 0
            _, single_beam_element_init = self.getBeamElementInX(x)
            for load in self.loads:
                _, single_beam_element = self.getBeamElementInX(load.x_begin+e)
                l_value = -load.momentum * \
                    cond(x-load.x_begin, order=1) if load.x_begin == load.x_end else 0
                l_value += load.force * \
                    cond(x-load.x_begin, order=2)/2 if load.order == 0 else 0
                l_value += (load.q*cond(x-load.x_begin, order=load.order+2) -
                            load.q*cond(x-load.x_end, order=load.order+2))/((load.order+1)*(load.order+2))
                f_value += l_value/single_beam_element.flexural_rigidity
                
            if not hasattr(self, "_c1"):
                return f_value*single_beam_element.flexural_rigidity
            return f_value + self._c1/single_beam_element_init.flexural_rigidity
        
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getRotation(x_element) for x_element in x ])
    
    def getRotationDiagram(self, **options):
        return self._createDiagram(self.getRotation, **options)
    
    def _createDiagram(self, function, division=1000, x_begin="begin", x_end="end"):
        x_begin = self.x_begin+e if x_begin=="begin" else x_begin
        x_end = self.x_end-e if x_end=="end" else x_end
        x = np.linspace(x_begin, x_end, division)
        y = np.array([function(x_i) for x_i in x])
        return x, y
    
    def plotMomentumDiagram(self, **options):
        x, y = self.getMomentumDiagram(**options)
        plt.gca().invert_yaxis()
        plt.plot(x, y)
        
    def plotShearDiagram(self, **options):
        x, y = self.getShearDiagram(**options)
        plt.plot(x, y)
        
    def plotDisplacementDiagram(self, **options):
        x, y = self.getDisplacementDiagram(**options)
        plt.plot(x, y)
        
    def plotRotationDiagram(self, **options):
        x, y = self.getRotationDiagram(**options)
        plt.plot(x, y)
    
    def __name__():
        return "Beam"
    
    def __repr__(self):
        return str(self.__dict__)

    def copy(self):
        return copy.deepcopy(self)
    
    def getDisplacement(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end: return 0
            f_value = 0
            _, single_beam_element_init = self.getBeamElementInX(x)
            
            for load in self.loads:
                _, single_beam_element = self.getBeamElementInX(x) #load.x_begin+e)
                l_value = -load.momentum * \
                    cond(x-load.x_begin, order=2)/2 if load.x_begin == load.x_end else 0
                l_value += load.force * \
                    cond(x-load.x_begin, order=3)/6 if load.order == 0 else 0
                l_value += (load.q*cond(x-load.x_begin, order=load.order+3) -
                            load.q*cond(x-load.x_end, order=load.order+3))/((load.order+1)*(load.order+2)*(load.order+3))
                f_value += l_value/single_beam_element.flexural_rigidity
            
            if not hasattr(self, "_c1"):
                return f_value*single_beam_element_init.flexural_rigidity
            
            return f_value + (self._c1*x+self._c2)/single_beam_element_init.flexural_rigidity
        
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getDisplacement(x_element) for x_element in x ])