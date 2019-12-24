from .Structural.Beam import Beam
import fconcrete
import numpy as np
import warnings
from scipy.signal import find_peaks
from .SteelBar import SteelBar


class ConcreteBeam(Beam):

    def __init__(self, loads, bars):
        Beam.__init__(self, loads, bars)
        self.steel = fconcrete.config.available_material['concrete_steel_bars']

        
        
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
        _, beam_element = self.getSingleBeamElementInX(x)
        return SteelBar.getMinimumAndMaximumSteelArea(
            area = beam_element.section.area,
            fck = beam_element.material.fck
        )


    def getSteelArea(self, x, momentum):
        #only working with rectangle section
        _, single_beam = self.getSingleBeamElementInX(x)
        return SteelBar.getSteelArea(section=single_beam.section,
                                           material=single_beam.section.material,
                                           steel=self.steel,
                                           momentum=momentum)
    
    def getComercialSteelArea(self, x, momentum):
        area = self.getSteelArea(x, momentum)
        if np.isnan(area): return np.repeat(np.nan, 3)
        if area>0 :
            possible_areas = self.steel.table[:,2] > area
            values = self.steel.table[possible_areas][0]
        else:
            possible_areas = self.steel.table[:,2] < area
            values = self.steel.table[possible_areas][-1]
        quantity, diameter, area = values
        return quantity, diameter, area

    
    def getSteelAreaDiagram(self, division=1000):
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDiagram(division)
        positive_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return x_decalaged, np.array(positive_areas), np.array(negative_areas)
        
    def getComercialSteelAreaDiagram(self, division=1000):
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDiagram(division)
        positive_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return x_decalaged, np.array(positive_areas_info).T, np.array(negative_areas_info).T
        
    def getSteelDiagram(self, division=1000):
        return self._createDiagram(self.getSteelArea, division)