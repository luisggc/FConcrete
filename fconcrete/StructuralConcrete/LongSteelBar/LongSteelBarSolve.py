import numpy as np
from .LongSteelBar import LongSteelBar, LongSteelBars
import warnings
#from scipy.signal import find_peaks
from .find_peaks import detect_peaks as find_peaks
from math import radians, sin, tan
from fconcrete.helpers import timeit, make_dxf, getAxis
import matplotlib.pyplot as plt

class LongSteelBarSolve():
    def __init__(self, concrete_beam):
        verbose = concrete_beam.verbose
        self.verbose = verbose
        self.available = concrete_beam.available_long_steel_bars
        self.concrete_beam = concrete_beam
        
        self.bar_steel_removal_step = self.concrete_beam.bar_steel_removal_step
        self.bar_steel_max_removal = self.concrete_beam.bar_steel_max_removal
        
        x, positive_areas_info, negative_areas_info = timeit(verbose)(self.getComercialSteelAreaDiagram)(division=concrete_beam.division)
        self.x = x
        self.positive_areas_info = positive_areas_info
        self.negative_areas_info = negative_areas_info
        
        interspace_between_momentum_positive = self._getInterspaceBetweenMomentum(x, area=positive_areas_info[2])
        interspace_between_momentum_negative = self._getInterspaceBetweenMomentum(x, area=negative_areas_info[2])
        
        self.interspace_between_momentum_positive = interspace_between_momentum_positive
        self.interspace_between_momentum_negative = interspace_between_momentum_negative
        
        steel_bars_positive = self._getBarsInInterspaces(x, positive_areas_info, interspace_between_momentum_positive)
        steel_bars_negative = self._getBarsInInterspaces(x, negative_areas_info, interspace_between_momentum_negative)
        #steel_bars_negative = self._getBarsInInterspaces(x, negative_areas_info, interspace_between_momentum_negative)
        
        concatenation = list(np.concatenate((steel_bars_positive.steel_bars,steel_bars_negative.steel_bars)))
        concatenation.sort(key=lambda x: x.long_begin, reverse=False)
        steel_bars = LongSteelBars(np.array(concatenation))
        
        steel_bars_with_anchor_length_positive = timeit(verbose, "Anchor positive steel bar")(self._anchorSteelBars)(steel_bars, interspace_between_momentum_positive)
        self.steel_bars = timeit(verbose, "Anchor negative steel bar")(self._anchorSteelBars)(steel_bars_with_anchor_length_positive, interspace_between_momentum_negative)
        
        
    def getDecalagedMomentumDesignDiagram(self, **options_diagram):
        """
            Returns tuple with 3 np.array: x (axis), momentum_positive, momentum_negative.
            
                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getDecalagedMomentumDesignDiagram(division=1000)

                >>> x_decalaged, momentum_positive, momentum_negative = concrete_beam.long_steel_bars_solution_info.getDecalagedMomentumDesignDiagram(division=100)
            
            Parameters
            ----------
            division : int, optional (default 1000)
                Define the step to plot the graph.
                A high number means a more precise graph, but also you need more processing time.
            
        """
        x, momentum_diagram = self.concrete_beam.getMomentumDiagram(division=self.concrete_beam.division)
        x_decalaged, decalaged_x_left, decalaged_x_right, join_decalaged_x_order = self.__decalageds_x_axis(x)
        momentum_positive, momentum_negative = self.__decalaged_momentums(x_decalaged,
                                                                    decalaged_x_left,
                                                                    decalaged_x_right,
                                                                    join_decalaged_x_order,
                                                                    momentum_diagram)
        momentum_positive = self.__join_momentum_peak(momentum_positive)
        momentum_negative = self.__join_momentum_peak(momentum_negative)
        
        return x_decalaged, self.concrete_beam.design_factor*momentum_positive, self.concrete_beam.design_factor*momentum_negative
    
    def plotDecalagedMomentumDesignDiagram(self, ax=None, fig=None, **options):
        """
            Plot DecalagedMomentumDesignDiagram.
        """
        fig, ax = getAxis() if ax == None else (fig, ax)
        ax.set_aspect("auto")
        
        x, momentum_positive, momentum_negative = self.getDecalagedMomentumDesignDiagram(**options)
        ax.plot(x, momentum_positive)
        ax.plot(x, momentum_negative)
        plt.gca().invert_yaxis()
        return make_dxf(ax, **options)
    
    def __decalageds_x_axis(self, x):
        decalaged_x_left = np.array([])
        decalaged_x_right = np.array([])
        
        for beam_element in self.concrete_beam.beam_elements:
            a_l = self.getDecalagedLength(beam_element)
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
        peaks = find_peaks(np.absolute(momentum))
        for peak_index in 2*np.arange(len(peaks)//2):
            x_momentum_index = peaks[peak_index]
            next_x_momentum_index = peaks[peak_index+1]
            momentum[x_momentum_index:next_x_momentum_index] = momentum[x_momentum_index]
        return momentum

    def getMinimumAndMaximumSteelArea(self, x):
        """
            Returns tuple of minimum and maximum necessary steel area given the position.

                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getMinimumAndMaximumSteelArea(x)

                >>> concrete_beam.long_steel_bars_solution_info.getMinimumAndMaximumSteelArea(300)
                (2.76, 19.2)
                
            Parameters
            ----------
            x : number
                Define the position in cm.
            
        """
        _, beam_element = self.concrete_beam.getBeamElementInX(x)
        return LongSteelBar.getMinimumAndMaximumSteelArea(
            area = beam_element.section.area,
            fck = beam_element.material.fck
        )
        
        
    
    def getComercialSteelAreaDiagram(self, **options_diagram):
        """
            Returns comercial steel area diagram.
            Implements: minimum steel area, check maximum steel area and do not allow a single steel bar.
            Does not have the removal by step implemented here.

                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getComercialSteelAreaDiagram(division=1000)

                >>> x_decalaged, positive_areas_info, negative_areas_info = concrete_beam.long_steel_bars_solution_info.getComercialSteelAreaDiagram()
                >>> x_decalaged, positive_areas_info, negative_areas_info = concrete_beam.long_steel_bars_solution_info.getComercialSteelAreaDiagram(division=5000)
        """ 
        x_decalaged, momentum_positive, momentum_negative = timeit(self.verbose)(self.getDecalagedMomentumDesignDiagram)(**options_diagram)
        positive_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        
        #positive_areas_info = timeit("positive_areas_info", self.verbose)([self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)])
        #negative_areas_info = timeit("negative_areas_info", self.verbose)([self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)])
        return x_decalaged, np.array(np.array(positive_areas_info).T), np.array(np.array(negative_areas_info).T)

    
    def getComercialSteelArea(self, x, momentum):
        """
            Returns comercial steel area given the position and momentum.
            Implements: minimum steel area, check maximum steel area and do not allow a single steel bar.
            Does not have the removal by step implemented here.
            Not recommended to use in loops.

                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getComercialSteelArea(x, momentum)

                >>> concrete_beam.long_steel_bars_solution_info.getComercialSteelArea(300, 2500)
                (6.0, 0.8, 3.0)
                
            Parameters
            ----------
            x : number
                Define the position in cm.
                
            momentum : number
                Define the momentum in kNcm.
            
        """ 
        min_area, max_area = self.getMinimumAndMaximumSteelArea(x)
        area = self.getSteelArea(x, momentum)
        
        # Implement minimun area in support
        
        if abs(area)>max_area: raise Exception("Too much steel needed in x={}, area needed is {}cmˆ2, but the maximum is {}cmˆ2".format(x, abs(area), max_area))
        
        if np.isnan(area): return np.repeat(np.nan, 3)
        if area>0 :
            area = max(min_area, area)
            possible_areas = self.available.table[:,2] > area
            if len(possible_areas)==0: raise Exception("There is not a possible available longitudinal steel bar. You should try to increase max_number of fc.AvailableLongConcreteSteelBar.")
            values = self.available.table[possible_areas][0]
        else:
            possible_areas = self.available.table[:,2] < area
            if len(possible_areas)==0: raise Exception("There is not a possible available longitudinal steel bar. You should try to increase max_number of fc.AvailableLongConcreteSteelBar.")
            values = self.available.table[possible_areas][-1]
        quantity, diameter, area = values
        return quantity, diameter, area
    
    def _anchorSteelBars(self, steel_bars, interspace_between_momentum):
        steel_bar_surface_type = self.concrete_beam.available_long_steel_bars.surface_type
        n1 = (2.25 if steel_bar_surface_type == "ribbed"
        else 1 if steel_bar_surface_type == "plain"
        else 1.4 if steel_bar_surface_type == "carved"
        else 0)
                
        for interspace in interspace_between_momentum:
            steel_bars_in_insterspace = LongSteelBars(steel_bars[(interspace == steel_bars.interspaces).sum(axis=1)== 2])
            major_steel_bar = steel_bars_in_insterspace[abs(steel_bars_in_insterspace.areas_accumulated) == abs(steel_bars_in_insterspace.areas_accumulated).max()][0]
            diameter = major_steel_bar.diameter
            begin, end = major_steel_bar.long_begin, major_steel_bar.long_end
            _, bar_element = self.concrete_beam.getBeamElementInX((begin+end)/2)
            
            is_in_the_beam_element = (self.x >= begin) &  (self.x <= end)
            positive_area_info = self.positive_areas_info[:, is_in_the_beam_element]
            negative_area_info = self.negative_areas_info[:, is_in_the_beam_element]

            positive_area_diagram = positive_area_info[2]
            negative_area_diagram = negative_area_info[2]
            positive_area_diagram = positive_area_diagram[~np.isnan(positive_area_diagram)]
            negative_area_diagram = negative_area_diagram[~np.isnan(negative_area_diagram)]
            
            As_calc = max(positive_area_diagram.min(initial=0), negative_area_diagram.min(initial=0),
                        positive_area_diagram.max(initial=0), negative_area_diagram.max(initial=0), key=abs)

            As_ef = major_steel_bar.area_accumulated

            # Can make a more precise calculus here.
            # 1 if (h < 60 and bar_transv_y <= 30) or
            # (h >= 60 and bar_transv_y <= h-30) else 0.7
            n2 = 1 if major_steel_bar.area > 0 else 0.7
            n3 = 1 if diameter < 3.2 else (13.2 - diameter)/10

            f_bd = n1 * n2 * n3 * bar_element.material.fctd

            # Check if hook is necessary
            alpha = 0.7 if (begin <= self.concrete_beam.x_begin+bar_element.material.c or end >= self.concrete_beam.x_end-bar_element.material.c) else 1

            lb = max(abs(diameter*major_steel_bar.fyd/(4*f_bd)), 25*diameter)
            lbmin = max(0.3*lb, 10*diameter, 10)
            lb_nec = max(alpha*lb*As_calc/As_ef, lbmin)

            if f_bd ==0: raise Exception("fbd as zero")

            steel_bars = steel_bars.changeProperty("long_begin",
                                                   function=lambda x:x-lb_nec,
                                                   conditional=lambda x:list(x.interspace)==list(interspace))
            steel_bars = steel_bars.changeProperty("long_end",
                                                   function=lambda x:x+lb_nec,
                                                   conditional=lambda x:list(x.interspace)==list(interspace))
            
        return steel_bars


    def _getBarsInInterspaces(self, x, areas_info, interspaceBetweenMomentum):
        quantities, diameters, _ = areas_info  
        bar_steel_removal_step = self.bar_steel_removal_step
        bar_steel_max_removal = self.bar_steel_max_removal
        
        bars = LongSteelBars()
        for interspace in interspaceBetweenMomentum:
            bars_interspace = LongSteelBars()
            times_removal_occurred = 0
            
            #commum interspace info
            interspace_start, interspace_end = interspace[0], interspace[1]
            is_in_interpace = (x > interspace_start) & (x<interspace_end)
            x_interspace = x[is_in_interpace]
            quantities_interspace = quantities[is_in_interpace]
            diameter = diameters[is_in_interpace][0]
            
            max_quantity_interspace = int(max(quantities_interspace))
            min_quantity_interspace = int(min(quantities_interspace))
                    
            for quantity in range(1, max_quantity_interspace+1):
                if np.isin(quantity, bars_interspace.quantities_accumulated): continue
                x_same_quantity = x_interspace[quantities_interspace == quantity]
                if len(x_same_quantity)>0:
                    # Just removing bars according to bar_steel_removal_step
                    reminder = (quantity-min_quantity_interspace)%bar_steel_removal_step
                    quantity_accumulated = min(quantity - reminder + (reminder>0)*self.bar_steel_removal_step, max_quantity_interspace)
                    new_reminder = (quantity_accumulated-min_quantity_interspace)%bar_steel_removal_step
                    new_quantity = bar_steel_removal_step-new_reminder if min_quantity_interspace!=quantity_accumulated else min_quantity_interspace
                    
                    removal_limit_reached = times_removal_occurred>=bar_steel_max_removal-1
                    
                    
                    quantity = new_quantity if not removal_limit_reached else new_quantity+max_quantity_interspace-quantity_accumulated
                    quantity_accumulated = quantity_accumulated if not removal_limit_reached else max_quantity_interspace
        
                    area_accumulated = self.available.diameters_to_area[abs(diameter*10)]*quantity_accumulated*(1 if diameter>0 else -1)
                    fyd = self.available.fyd
                    area = self.available.diameters_to_area[abs(diameter*10)]*quantity*(1 if diameter>0 else -1)
                    long_begin = min(x_same_quantity)
                    long_end = max(x_same_quantity)
                    length = long_end-long_begin
                    cost = quantity*length*self.available.cost_by_meter[abs(diameter*10)]/100

                    new_bar = LongSteelBar(
                                    long_begin=long_begin,
                                    long_end=long_end,
                                    quantity=quantity,
                                    diameter=diameter,
                                    quantity_accumulated = quantity_accumulated,
                                    interspace=(interspace_start, interspace_end),
                                    area = area,
                                    area_accumulated = area_accumulated,
                                    fyd = fyd,
                                    length=length,
                                    cost = cost
                                    )
                    
                    bars_interspace.add(new_bar)
                    times_removal_occurred+=1
                    
                    if removal_limit_reached:
                        break
                    
            bars.add(bars_interspace)

        return bars
    
    #con be static
    def _getInterspaceBetweenMomentum(self, x, area):
        """
            Return an array and each row represents a interspace.
            Element row[0] is the begin of interspace and row[1], the end.
        """
        previous_y=np.nan
        interspace = np.array([0, 0])
        if sum(np.isfinite(area)) == 0 : return []
        for x_u,y in zip(x, area):
            if np.isnan(previous_y) and not np.isnan(y):
                begin = x_u
            elif np.isnan(y) and not np.isnan(previous_y):
                end = x_u
                interspace = np.vstack([interspace, [begin, end]])
            previous_y = y
        interspace = np.vstack([interspace, [begin, x[-1]]])[1:]
        return interspace


    def getSteelArea(self, x, momentum):
            """
                #only working with rectangle section
                Returns necessary steel area given the position and momentum.

                    Call signatures:

                        concrete_beam.long_steel_bars_solution_info.getSteelArea(x, momentum)

                    >>> concrete_beam.long_steel_bars_solution_info.getSteelArea(10, 2500)
                    0.903512040037519
                    
                Parameters
                ----------
                x : number
                    Define the position in cm.
                    
                momentum : number
                    Define the momentum in kNcm.
                
            """ 
            #only working with rectangle section
            _, single_beam = self.concrete_beam.getBeamElementInX(x)
            return LongSteelBar.getSteelArea(section=single_beam.section,
                                            material=single_beam.material,
                                            steel=self.available,
                                            momentum=momentum)
        
        
    def getSteelAreaDiagram(self, **options_diagram):
        """
            Returns necessary steel area diagram.

                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getSteelAreaDiagram(division=1000)

                >>> x_decalaged, positive_areas, negative_areas = concrete_beam.long_steel_bars_solution_info.getSteelAreaDiagram()
                >>> x_decalaged, positive_areas, negative_areas = concrete_beam.long_steel_bars_solution_info.getSteelAreaDiagram(division=20)
            
        """ 
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDesignDiagram(**options_diagram)
        positive_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return x_decalaged, np.array(positive_areas), np.array(negative_areas)
    
    
    def getDecalagedLength(self, beam_element):
        """
            Returns decalaged length of a beam element.

                Call signatures:

                    concrete_beam.long_steel_bars_solution_info.getDecalagedLength(beam_element)
        """ 
        bw = beam_element.section.bw
        d = beam_element.section.maximum_steel_height
        _, s = self.concrete_beam.getShearDiagram(x_begin=beam_element.n1.x, x_end=beam_element.n2.x)
        alpha = radians(self.concrete_beam.available_transv_steel_bars.inclination_angle)
        if alpha==radians(90):
            return 0.5*d
        vsd_max = max(abs(s))
        fctd = beam_element.material.fctd
        v_c0 = 0.6*fctd*bw*d
        al_formula = min(d*((vsd_max*(1+tan(alpha)**(-1)))/(2*(vsd_max-v_c0))-tan(alpha)**(-1)), d)
        if vsd_max <= v_c0:
            al = d
        elif alpha==radians(45):
            al = max(al_formula, 0.2*d)
        return al
    
    
    