from .Structural.Beam import Beam
import fconcrete
import numpy as np
import warnings
from scipy.signal import find_peaks
from .LongSteelBar import LongSteelBar, LongSteelBars


class ConcreteBeam(Beam):

    def __init__(self, loads, beam_elements,
                 bar_steel_removal_step=2, bar_steel_max_removal=100, design_factor=1.4, division=1000,
                 **options):
        """
            Returns a concrete_beam element.
            
                Call signatures::

                    concrete_beam.getDecalagedMomentumDesignDiagram(self, loads, bars, bar_steel_removal_step=2, **options)

                
                >>>    material = fc.Concrete(fck='20 MPa', aggressiveness=2)
                >>>    section = fc.Rectangle(25,56, material)

                >>>    f1 = fc.Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
                >>>    f2 = fc.Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
                >>>    f3 = fc.Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

                >>>    n1 = fc.Node.SimpleSupport(x=0)
                >>>    n2 = fc.Node.SimpleSupport(x=113)
                >>>    n3 = fc.Node.SimpleSupport(x=583)
                >>>    n4 = fc.Node.SimpleSupport(x=1188)

                >>>    beam_element1 = fc.SingleBeamElement([n1, n2], section)
                >>>    beam_element2 = fc.SingleBeamElement([n2, n3], section)
                >>>    beam_element3 = fc.SingleBeamElement([n3, n4], section)

                >>>    fc.ConcreteBeam(
                        loads = [f1, f2, f3],
                        beam_elements = [beam_element1, beam_element2, beam_element3],
                        bar_steel_removal_step = 2,
                        bar_steel_max_removal = 100
                    )
            
            Parameters
            ----------
            loads : [Load]
                Define the loads supported for the beam.
            
            beam_elements : [Load]
                Define the beam_elements that, together, makes the whole Beam. 
            
            bar_steel_removal_step: int, optional (default 2)
                Define the step during the removal of the bar. Instead of taking the steel bars one by one, the bar_steel_removal_step will make the removal less constant.
                I makes the building process easier. 
                
            bar_steel_max_removal: int, optional (default 100)
                Define the max times it is possible to remove the bar.
                
            
        """
        
        Beam.__init__(self, loads, beam_elements, **options)
        self.steel = fconcrete.config.available_material['concrete_long_steel_bars']
        self.bar_steel_removal_step = bar_steel_removal_step
        self.bar_steel_max_removal = bar_steel_max_removal
        self.design_factor = design_factor
        self.division = division
        
        if options.get("solve_long_steel") != False:
            self.steel_bars = self.solve_long_steel()
        
        if options.get("solve_transv_steel") != False:
            solution_info = fconcrete.TransvSteelBarSolve(concrete_beam=self, fyk=50, theta_in_degree=45, alpha_in_degree = 90)
            self.transv_steel_bars = solution_info.steel_bars
        
    def getDecalagedMomentumDesignDiagram(self, **options_diagram):
        """
            Returns tuple with 3 np.array: x (axis), momentum_positive, momentum_negative.
            

                Call signatures::

                    concrete_beam.getDecalagedMomentumDesignDiagram(division=1000)

                >>> concrete_beam.getDecalagedMomentumDesignDiagram(5000)
            
            Parameters
            ----------
            division : int, optional (default 1000)
                Define the step to plot the graph.
                A high number means a more precise graph, but also you need more processing time.
            
        """
        x, momentum_diagram = self.getMomentumDiagram(division=self.division)
        x_decalaged, decalaged_x_left, decalaged_x_right, join_decalaged_x_order = self.__decalageds_x_axis(x)
        momentum_positive, momentum_negative = self.__decalaged_momentums(x_decalaged,
                                                                    decalaged_x_left,
                                                                    decalaged_x_right,
                                                                    join_decalaged_x_order,
                                                                    momentum_diagram)
        momentum_positive = self.__join_momentum_peak(momentum_positive)
        momentum_negative = self.__join_momentum_peak(momentum_negative)
        
        return x_decalaged, self.design_factor*momentum_positive, self.design_factor*momentum_negative
    
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
        """
            Returns tuple of minimum and maximum necessary steel area given the position.

                Call signatures::

                    concrete_beam.getMinimumAndMaximumSteelArea(x)

                >>> concrete_beam.getMinimumAndMaximumSteelArea(300)

            Parameters
            ----------
            x : number
                Define the position in cm.
            
        """
        _, beam_element = self.getSingleBeamElementInX(x)
        return LongSteelBar.getMinimumAndMaximumSteelArea(
            area = beam_element.section.area,
            fck = beam_element.material.fck
        )


    def getSteelArea(self, x, momentum):
        """
            #only working with rectangle section
            Returns necessary steel area given the position and momentum.

                Call signatures::

                    concrete_beam.getSteelArea(x, momentum)

                >>> concrete_beam.getSteelArea(300, 250000)

            Parameters
            ----------
            x : number
                Define the position in cm.
                
            momentum : number
                Define the momentum in kNcm.
            
        """ 
        #only working with rectangle section
        _, single_beam = self.getSingleBeamElementInX(x)
        return LongSteelBar.getSteelArea(section=single_beam.section,
                                           material=single_beam.section.material,
                                           steel=self.steel,
                                           momentum=momentum)
    
    def getComercialSteelArea(self, x, momentum):
        """
            Returns comercial steel area given the position and momentum.
            Implements: minimum steel area, check maximum steel area and do not allow a single steel bar.
            Does not have the removal by step implemented here.

                Call signatures::

                    concrete_beam.getComercialSteelArea(x, momentum)

                >>> concrete_beam.getComercialSteelArea(300, 250000)

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
            possible_areas = self.steel.table[:,2] > area
            values = self.steel.table[possible_areas][0]
        else:
            possible_areas = self.steel.table[:,2] < area
            values = self.steel.table[possible_areas][-1]
        quantity, diameter, area = values
        return quantity, diameter, area

    
        
    def getComercialSteelAreaDiagram(self, **options_diagram):
        """
            Returns comercial steel area diagram.
            Implements: minimum steel area, check maximum steel area and do not allow a single steel bar.
            Does not have the removal by step implemented here.

                Call signatures::

                    concrete_beam.getComercialSteelAreaDiagram(division=1000)

                >>> x_decalaged, positive_areas_info, negative_areas_info = concrete_beam.getComercialSteelAreaDiagram()
                >>> x_decalaged, positive_areas_info, negative_areas_info = concrete_beam.getComercialSteelAreaDiagram(5000)

            Parameters
            ----------
            division : int, optional (default 1000)
                Define the step to plot the graph.
                A high number means a more precise graph, but also you need more processing time.
            
        """ 
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDesignDiagram(**options_diagram)
        positive_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas_info = [self.getComercialSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return (x_decalaged,np.array(positive_areas_info).T,np.array(negative_areas_info).T)


    def getSteelAreaDiagram(self, return_positive_and_negative=False, **options_diagram):
        """
            Returns necessary steel area diagram.

                Call signatures::

                    concrete_beam.getSteelDiagram(division=1000)

                >>> concrete_beam.getSteelDiagram()
                >>> concrete_beam.getSteelDiagram(5000)

            Parameters
            ----------
            division : int, optional (default 1000)
                Define the step to plot the graph.
                A high number means a more precise graph, but also you need more processing time.
            
        """ 
        #if return_positive_and_negative:
        x_decalaged, momentum_positive, momentum_negative = self.getDecalagedMomentumDesignDiagram(**options_diagram)
        positive_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_positive)]
        negative_areas = [self.getSteelArea(x, m) for x, m in zip(x_decalaged, momentum_negative)]
        return x_decalaged, np.array(positive_areas), np.array(negative_areas)
        #else:
        #    return self._createDiagram(self.getSteelArea)
    
    def _getInterspaceBetweenMomentum(self, x, area):
        """
            Return an array and each row represents a interspace.
            Element row[0] is the begin of interspace and row[1], the end.
        """
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
                    
                    new_bar = LongSteelBar(long_begin=min(x_same_quantity),
                                    long_end=max(x_same_quantity),
                                    quantity=new_quantity if not removal_limit_reached else new_quantity+max_quantity_interspace-quantity_accumulated,
                                    diameter=diameter,
                                    quantity_accumulated = quantity_accumulated if not removal_limit_reached else max_quantity_interspace,
                                    interspace=(interspace_start, interspace_end)
                                    )
                    
                    bars_interspace.add(new_bar)
                    times_removal_occurred+=1
                    
                    if removal_limit_reached:
                        break
                    
            bars.add(bars_interspace)

        return bars
    
    def _anchorSteelBars(self, steel_bars, interspace_between_momentum):
        steel_bar_surface_type = fconcrete.config.available_material["concrete_long_steel_bars"].steel_bar_surface_type
        n1 = (2.25 if steel_bar_surface_type == "ribbed"
        else 1 if steel_bar_surface_type == "plain"
        else 1.4 if steel_bar_surface_type == "carved"
        else 0)
                
        for interspace in interspace_between_momentum:
            steel_bars_in_insterspace = fconcrete.LongSteelBars(steel_bars[(interspace == steel_bars.interspaces).sum(axis=1)== 2])
            major_steel_bar = steel_bars_in_insterspace[abs(steel_bars_in_insterspace.areas_accumulated) == abs(steel_bars_in_insterspace.areas_accumulated).max()][0]
            diameter = major_steel_bar.diameter
            begin, end = major_steel_bar.long_begin, major_steel_bar.long_end
            _, bar_element = self.getSingleBeamElementInX((begin+end)/2)
            _, positive_area_diagram, negative_area_diagram = self.getSteelAreaDiagram(division=100,
                                                                                    x_begin= begin if begin>self.x_begin else self.x_begin,
                                                                                    x_end= end if end<self.x_end else self.x_end)
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

            f_bd = n1 * n2 * n3 * bar_element.section.material.fctd

            # Check if hook is necessary
            alpha = 0.7 if (begin <= self.x_begin+bar_element.section.material.c or end >= self.x_end-bar_element.section.material.c) else 1

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

    
    def solve_long_steel(self):
        x, positive_areas_info, negative_areas_info = self.getComercialSteelAreaDiagram(division=self.division)
        
        interspace_between_momentum_positive = self._getInterspaceBetweenMomentum(x, positive_areas_info[2])
        interspace_between_momentum_negative = self._getInterspaceBetweenMomentum(x, negative_areas_info[2])
        
        self.interspace_between_momentum_positive = interspace_between_momentum_positive
        self.interspace_between_momentum_negative = interspace_between_momentum_negative
        
        steel_bars_positive = self._getBarsInInterspaces(x, positive_areas_info, interspace_between_momentum_positive)
        steel_bars_negative = self._getBarsInInterspaces(x, negative_areas_info, interspace_between_momentum_negative)
        
        concatenation = list(np.concatenate((steel_bars_positive.steel_bars,steel_bars_negative.steel_bars)))
        concatenation.sort(key=lambda x: x.long_begin, reverse=False)
        steel_bars = LongSteelBars(np.array(concatenation))
        
        steel_bars_with_anchor_length_positive = self._anchorSteelBars(steel_bars, interspace_between_momentum_positive)
        steel_bars_with_anchor_length = self._anchorSteelBars(steel_bars_with_anchor_length_positive, interspace_between_momentum_negative)
        
        return steel_bars_with_anchor_length
    
    def getShearDesignDiagram(self, **options_diagram):
        x, shear_diagram = self.getShearDiagram(division=self.division)
        return x, self.design_factor*shear_diagram
    
    
    
    
   