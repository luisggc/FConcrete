from fconcrete.Structural.SingleBeamElement import SingleBeamElement, SingleBeamElements
from fconcrete.Structural.Load import Load, Loads
from fconcrete.Structural.Node import Nodes
from fconcrete.ConcreteSteels import ConcreteSteels
from fconcrete.helpers import *
from fconcrete import e
import numpy as np
import warnings
from scipy.signal import find_peaks

class Beam:

    def __init__(self, loads, bars, steel=ConcreteSteels()):

        bars = SingleBeamElements.create(bars)
        loads = Loads.create(loads)
        bars = self.createIntermediateBeams(loads, bars)

        self.loads = loads
        self.bars = bars
        self.steel = steel
        
        self.length = sum(bars.length)
        self.beams_quantity = len(bars.bar_elements)
        
        # Nodes info
        nodal_efforts = self.getSupportReactions()
        self.nodal_efforts = nodal_efforts
        nodes = Nodes(self.bars.nodes)
        self.nodes = nodes

        #self.loads = Loads.create(self.loads.loads[self.loads.order>0])
        for index, node in enumerate(nodes.nodes):
            self.loads = self.loads.add(
                [Load(nodal_efforts[index*2], nodal_efforts[index*2+1], node.x, node.x)])

    @staticmethod
    def createIntermediateBeams(loads, bars):
        for load in loads.loads:
            bars = bars.split(load.x_begin)
            bars = bars.split(load.x_end)
        return bars

    def __matrix_rigidity_global(self):
        matrix_rigidity_row = 2*self.beams_quantity+2
        matrix_rigidity_global = np.zeros(
            (matrix_rigidity_row, matrix_rigidity_row))
        for beam_n, beam in enumerate(self.bars.bar_elements):
            matrix_rigidity_global[beam_n*2:beam_n*2+4,
                                   beam_n*2:beam_n*2+4] += beam.get_matrix_rigidity_unitary()
        return matrix_rigidity_global

    def __get_beams_efforts(self):
        beams_efforts = np.zeros(self.beams_quantity*4)

        for force in self.loads.loads:
            if (force.x == self.length):
                force.x = self.length - 0.0000000000001
            force_beam, beam_element = self.getSingleBeamElementInX(force.x)

            force_distance_from_nearest_left_node = force.x - \
                beam_element.x[0].x

            beams_efforts[4*force_beam:4*force_beam+4] += SingleBeamElement.get_efforts_from_bar_element(
                force.force,
                force_distance_from_nearest_left_node,
                beam_element.length
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
        beams_efforts = self.__get_beams_efforts()
        matrix_rigidity_global = self.__matrix_rigidity_global()

        matrix_rigidity_global_determinable = matrix_rigidity_global[
            condition_boundary, :][:, condition_boundary]
        beams_efforts_determinable = beams_efforts[condition_boundary]

        U = np.zeros(len(condition_boundary))
        U[condition_boundary] = np.linalg.solve(
            matrix_rigidity_global_determinable, beams_efforts_determinable)
        F = matrix_rigidity_global @ U

        return beams_efforts - F

    def getSingleBeamElementInX(self, x):
        index = 0 if x<self.bars.nodes[0].x else -1 if x>self.bars.nodes[-1].x else np.where(
            np.array([node.x for node in self.bars.nodes]) <= x)[0][-1]
        bar_element = self.bars.bar_elements[index]
        return index, bar_element
    
    def getInternalShearStrength(self, x):
        if x < self.bars.nodes[0].x or x > self.bars.nodes[-1].x:
            return 0
        f_value = 0
        for load in self.loads.loads:
            f_value += load.force * \
                cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
            f_value += load.q*cond(x-load.x_begin, order=load.order) - load.q*cond(
                x-load.x_end, order=load.order) if load.x_begin != load.x_end else 0
        return f_value

    def getShearDiagram(self, division=1000):
        x = np.linspace(self.bars.nodes[0].x-e,
                        self.bars.nodes[-1].x+e, division)
        y = [self.getInternalShearStrength(x_i) for x_i in x]
        return x, y

    def getInternalMomentumStrength(self, x):
        if x < self.bars.nodes[0].x or x > self.bars.nodes[-1].x:
            return 0
        f_value = 0
        for load in self.loads.loads:
            f_value += load.momentum * \
                cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
            f_value += load.force * \
                cond(x-load.x_begin, order=1) if load.order == 0 else 0
            f_value += (load.q*cond(x-load.x_begin, order=load.order+1) -
                        load.q*cond(x-load.x_end, order=load.order+1))/(load.order+1)
        return f_value
        
    def getMomentumDiagram(self, division=1000):
        return self.__createDiagram(self.getInternalMomentumStrength, division)

    def getDecalagedMomentumDiagram(self, division=1000):
        x, momentum_diagram = self.getMomentumDiagram(division)
        x_decalaged, decalaged_x_left, decalaged_x_right, join_decalaged_x_order = self.__decalageds_x_axis(x)
        momentum_positive, momentum_negative = self.__decalaged_momentums(x_decalaged,
                                                                    decalaged_x_left,
                                                                    decalaged_x_right,
                                                                    join_decalaged_x_order,
                                                                    momentum_diagram)
        momentum_positive = self.__join_momentum_peak(momentum_positive)
        momentum_negative = self.__join_momentum_peak(momentum_negative)
        
        return x_decalaged, momentum_positive, momentum_negative
    
    def __decalageds_x_axis(self, x):
        decalaged_x_left = np.array([])
        decalaged_x_right = np.array([])
        warnings.warn("Must improve a_l calculus", DeprecationWarning)
        for beam_element in self.bars:
            a_l = 0.5*beam_element.section.d
            position_in_beam_element = x[(x>=beam_element.n1.x) & (x<=beam_element.n2.x)]
            decalaged_x_left_temp = position_in_beam_element - a_l
            decalaged_x_right_temp = position_in_beam_element + a_l
            decalaged_x_left = np.concatenate((decalaged_x_left, decalaged_x_left_temp))
            decalaged_x_right = np.concatenate((decalaged_x_right, decalaged_x_right_temp))
        
        join_decalaged_x = np.concatenate((decalaged_x_left, x, decalaged_x_right))
        join_decalaged_x_order = join_decalaged_x.argsort()
        x_decalaged = join_decalaged_x[join_decalaged_x_order]
        
        return x_decalaged, decalaged_x_left, decalaged_x_right, join_decalaged_x_order

    @staticmethod
    def __decalaged_momentums(x_decalaged,
                              decalaged_x_left,
                              decalaged_x_right,
                              join_decalaged_x_order,
                              momentum_diagram):
        #momentum_decalaged_diagram = np.concatenate((momentum_diagram, momentum_diagram, momentum_diagram))[join_decalaged_x_order]

        momentum_left = np.interp(x_decalaged, decalaged_x_left, momentum_diagram)
        momentum_right = np.interp(x_decalaged, decalaged_x_right, momentum_diagram)

        momentum_positive = np.max((momentum_left, momentum_right), axis=0)
        momentum_positive = np.where(momentum_positive<0, np.nan, momentum_positive)
        
        momentum_negative = np.min((momentum_left, momentum_right), axis=0)
        momentum_negative = np.where(momentum_negative>0, np.nan, momentum_negative)
        return momentum_positive, momentum_negative  
        
    @staticmethod
    def __join_momentum_peak(_momentum):
        momentum = _momentum.copy() 
        peaks, _ = find_peaks(np.absolute(momentum))
        for peak_index in 2*np.arange(len(peaks)//2):
            x_momentum_index = peaks[peak_index]
            next_x_momentum_index = peaks[peak_index+1]
            momentum[x_momentum_index:next_x_momentum_index] = momentum[x_momentum_index]
        return momentum

    def getMinimumAndMaximumSteelArea(self, x):
        index, beam_element = self.getSingleBeamElementInX(x)
        area = beam_element.section.area
        fck = beam_element.material.fck
        #md_min = 0.8*w_o*fctk_sup
        fck_array = 20 + 5*np.arange(15)
        p_min_array = np.array([ 0.15, 1.15, 1.15, 1.164, 0.179, 0.194, 0.208, 0.211, 0.219, 0.226, 0.233, 0.239, 0.245, 0.251, 0.256])
        p_min = np.interp(fck, fck_array, p_min_array)
        A_min = area*p_min/100
        A_max = 0.008*area
        return A_min, A_max


    def getSteelArea(self, x, momentum):
        #only working with rectangle section
        index_beam, single_beam = self.getSingleBeamElementInX(x)
        return ConcreteSteels.getSteelArea(section=single_beam.section,
                                           material=single_beam.section.material,
                                           steel=self.steel,
                                           momentum=momentum)
    
    def getComercialSteelArea(self, x, momentum):
        area = self.getSteelArea(x, momentum)
        if area>0 :
            possible_areas = self.steel.table[:,2] > area
            return self.steel.table[possible_areas][0]
        else:
            possible_areas = self.steel.table[:,2] < area
            return self.steel.table[possible_areas][-1]
    
    def getSteelAreaDiagram(self, division=1000):
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDiagram(division)
        positive_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return x_decalaged, positive_areas, negative_areas
        
    def getComercialSteelAreaDiagram(self, division=1000):
        return self.__createDiagram(self.getComercialSteelArea, division)
    
    def getSteelDiagram(self, division=1000):
        return self.__createDiagram(self.getSteelArea)
    
    def __createDiagram(self, function, division=1000):
        x = np.linspace(self.bars.nodes[0].x+e, self.bars.nodes[-1].x-e, division)
        y = np.array([function(x_i) for x_i in x])
        return x, y
    
    def __repr__(self):
        return str(self.__dict__)
