from fconcrete.Structural.SingleBeamElement import SingleBeamElement, SingleBeamElements
from fconcrete.Structural.Load import Load, Loads
from fconcrete.Structural.Node import Nodes
from fconcrete.helpers import cond
import numpy as np
import warnings
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

class Beam:

    def __init__(self, loads, bars, **options):
        from fconcrete import config
        globals()['e'] = config.e
        bars = SingleBeamElements.create(bars)
        external_loads = Loads.create(loads)
        bars = self.createIntermediateBeams(external_loads, bars)

        self.external_loads = external_loads
        self.bars = bars
        
        self.length = sum(bars.length)
        self.beams_quantity = len(bars.bar_elements)
        
        if options.get("solve_structural") != False:
            self.solve_structural()
        
        
    def solve_structural(self):
        nodal_efforts = self.getSupportReactions()
        self.nodal_efforts = nodal_efforts
        nodes = Nodes(self.bars.nodes)
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
        for beam_n, beam in enumerate(self.bars.bar_elements):
            matrix_rigidity_global[beam_n*2:beam_n*2+4,
                                   beam_n*2:beam_n*2+4] += beam.get_matrix_rigidity_unitary()
        return matrix_rigidity_global

    def get_beams_efforts(self):
        beams_efforts = np.zeros(self.beams_quantity*4)

        for load in self.external_loads.loads:
            if (load.x == self.length):
                load.x = self.length - e
            force_beam, beam_element = self.getSingleBeamElementInX(load.x)

            beams_efforts[4*force_beam:4*force_beam+4] += SingleBeamElement.get_efforts_from_bar_element(
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
        condition_boundary = self.bars.condition_boundary
        beams_efforts = self.get_beams_efforts()
        matrix_rigidity_global = self.matrix_rigidity_global()

        matrix_rigidity_global_determinable = matrix_rigidity_global[condition_boundary, :][:, condition_boundary]
        beams_efforts_determinable = beams_efforts[condition_boundary]

        U = np.zeros(len(condition_boundary))
        U[condition_boundary] = np.linalg.solve(matrix_rigidity_global_determinable, beams_efforts_determinable)
        #U[condition_boundary] = beams_efforts_determinable @ np.linalg.pinv(matrix_rigidity_global_determinable)
        
        F = matrix_rigidity_global @ U

        return beams_efforts - F
    

    def getSingleBeamElementInX(self, x):
        
            index = 0 if x<self.bars.nodes[0].x else -1 if x>self.bars.nodes[-1].x else np.where(
            np.array([node.x for node in self.bars.nodes]) <= x)[0][-1]
            bar_element = self.bars.bar_elements[index]
            return index, bar_element
        
    def getInternalShearStrength(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.bars.nodes[0].x or x > self.bars.nodes[-1].x:
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
        
    def getShearDiagram(self, division=1000):
        x = np.linspace(self.bars.nodes[0].x-e,
                        self.bars.nodes[-1].x+e, division)
        y = [self.getInternalShearStrength(x_i) for x_i in x]
        return x, y

    def getInternalMomentumStrength(self, x):
        if isinstance(x, int) or isinstance(x, float):
            if x < self.bars.nodes[0].x or x > self.bars.nodes[-1].x:
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
        
    def getMomentumDiagram(self, division=1000):
        return self._createDiagram(self.getInternalMomentumStrength, division)
    
    def _createDiagram(self, function, division=1000):
        x = np.linspace(self.bars.nodes[0].x+e, self.bars.nodes[-1].x-e, division)
        y = np.array([function(x_i) for x_i in x])
        return x, y
    
    def plotMomentumDiagram(self, division=1000):
        x, y = self.getMomentumDiagram(division)
        plt.gca().invert_yaxis()
        plt.plot(x, y)
        
    def plotShearDiagram(self, division=1000):
        x, y = self.getShearDiagram(division)
        plt.plot(x, y)
    
    def __repr__(self):
        return str(self.__dict__)
