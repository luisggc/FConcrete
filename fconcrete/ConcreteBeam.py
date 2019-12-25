from .Structural.Beam import Beam
import fconcrete
import numpy as np
import warnings
from scipy.signal import find_peaks
from .SteelBar import SteelBar, SteelBars


class ConcreteBeam(Beam):

    def __init__(self, loads, bars, bar_steel_removal_step=2, **options):
        Beam.__init__(self, loads, bars, **options)
        self.steel = fconcrete.config.available_material['concrete_steel_bars']
        self.bar_steel_removal_step = bar_steel_removal_step
        
        if options.get("solve_steel") != False:
            self.steel_bars = self.solve_steel()
        
        
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
        
        min_area, max_area = self.getMinimumAndMaximumSteelArea(x)
        area = self.getSteelArea(x, momentum)
        
        # Implement minimun area in support
        
        if abs(area)>max_area: raise Exception("Too much steel needed in x={}, area needed is {}cmˆ2, but the maximum is {}cmˆ2".format(x, abs(area), max_area))
        
        if np.isnan(area): return np.repeat(np.nan, 3)
        if area>0 :
            area = max(min_area, area)
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
    
    
    def _getInterspaceBetweenMomentum(self, x, area):
        '''
        Return an array and each row represents a interspace.
        Element row[0] is the begin of interspace and row[1], the end.
    '''
        previous_y=np.nan
        interspace = np.array([0, 0])
        for x_u,y in zip(x, area):
            if np.isnan(previous_y) and not np.isnan(y):
                begin = x_u
            elif np.isnan(y) and not np.isnan(previous_y):
                end = x_u
                interspace = np.vstack([interspace, [begin, end]])
            previous_y = y
        interspace = np.vstack([interspace, [begin, x[-1]]])[1:]
        return interspace


    def _getBarsInInterspaces(self, x, areas_info):
        quantities, diameters, areas = areas_info  
        bars = SteelBars()
        for interspace in self._getInterspaceBetweenMomentum(x, areas):
            bars_interspace = SteelBars()
            is_in_interpace = (x > interspace[0]) & (x<interspace[1])
            x_interspace = x[is_in_interpace]
            quantities_interspace = quantities[is_in_interpace]
            diameter = diameters[is_in_interpace][0]
            max_quantity_interspace = int(max(quantities_interspace))
            min_quantity_interspace = int(min(quantities_interspace))
                    
            for quantity in range(1, max_quantity_interspace+1):
                if np.isin(quantity, bars_interspace.quantities): continue
                x_same_quantity = x_interspace[quantities_interspace == quantity]
                if len(x_same_quantity)>0:
                    # Just removing bars according to bar_steel_removal_step
                    reminder = (quantity-min_quantity_interspace)%self.bar_steel_removal_step
                    new_quantity = min(quantity - reminder + (reminder>0)*self.bar_steel_removal_step, max_quantity_interspace)

                    new_bar = SteelBar(long_begin=min(x_same_quantity),
                                    long_end=max(x_same_quantity),
                                    quantity=new_quantity,
                                    diameter=diameter)
                    bars_interspace.add(new_bar)
            bars.add(bars_interspace)

        return bars
    
    
    def solve_steel(self):
        x, positive_areas_info, negative_areas_info = self.getComercialSteelAreaDiagram()
        steel_bars_positive = self._getBarsInInterspaces(x, positive_areas_info)
        steel_bars_negative = self._getBarsInInterspaces(x, negative_areas_info)
        
        
        
        
        concatenation = list(np.concatenate((steel_bars_positive.steel_bars,steel_bars_negative.steel_bars)))
        concatenation.sort(key=lambda x: x.long_begin, reverse=False)
        steel_bars = np.array(concatenation)
            
        return SteelBars(steel_bars)