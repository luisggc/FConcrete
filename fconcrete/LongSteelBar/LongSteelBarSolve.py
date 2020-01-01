import numpy as np
import fconcrete

class TransvSteelBarSolve():
    def __init__(self, concrete_beam):
        
        self.available = fconcrete.config.available_material["concrete_long_steel_bars"]
        
        
        
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

    
    
    
    
    
    
    
    @staticmethod
    def _getS_max(v_rd2, d, v_sd, available):
        s_max = min(0.6*d, 30) if v_sd <= 0.67*v_rd2 else min(0.3*d, 20)        
        return s_max
        
    def checkProbableCompressedConnectingRod(self):
        max_shear = max(self.shear_diagram)
        max_shear_x = self.x[self.shear_diagram == max_shear][0]
        max_section = self.concrete_beam.getSingleBeamElementInX(max_shear_x)[1].section
        v_rd2 = self.getV_rd2(max_section)
        check = max_shear <= v_rd2
        if check == False: raise Exception("Shear ({}kN) in x={} is greater or equal to maximum shear allowed ({}kN)".format(max_shear, max_shear_x, v_rd2))
        return v_rd2, max_section.d, max_shear
    
    def getV_rd2(self, section):
        fck = section.material.fck
        bw = section.bw
        d = section.d
        fcd = section.material.fcd
        alpha_v2 = (1-fck/25)
        v_rd2 = 0.54*alpha_v2*fcd*bw*d*(sin(self.theta))*(tan(self.alpha)**(-1)+tan(self.theta)**(-1))
        return v_rd2
    
    def getMinimumSteelAreaPerCm(self,section):
        fctm = section.material.fctm
        bw = section.bw
        As_per_cm_min = 0.2*fctm*bw*sin(self.alpha)/self.fyk
        return As_per_cm_min
    

    def getShearSteelAreaPerCm(self, x, v_sd): 
        # can be optimized
        section = self.concrete_beam.getSingleBeamElementInX(x)[1].section
        v_rd2 = self.getV_rd2(section)
        As_per_cm_min = self.getMinimumSteelAreaPerCm(section)
        
        _, single_beam_element = self.concrete_beam.getSingleBeamElementInX(x)
        bw = single_beam_element.section.bw
        d = single_beam_element.section.d
        fctd = single_beam_element.section.material.fctd

        v_c0 = 0.6*fctd*bw*d
        v_c1 = np.interp(v_sd, [v_c0, v_c0, v_rd2], [v_c0, v_c0, 0])
        v_c = v_c1
        v_sw = max(v_sd - v_c, 0)
        
        As_per_cm = v_sw/(0.9*d*self.fyd*(sin(self.alpha))*(tan(self.alpha)**(-1)+tan(self.theta)**(-1)))
        
        return max(As_per_cm, As_per_cm_min)

    def getShearSteelAreaPerCmDiagram(self):
        shear_area_per_cm = [self.getShearSteelAreaPerCm(x_u, v_sd) for x_u, v_sd in zip(self.x, self.shear_diagram)]
        return np.array(shear_area_per_cm)
    
    def getComercialInfo(self, as_per_cm):
        table = self.available.table
        diameter, space, area, as_per_cm = table[table[:, 3] >= as_per_cm][0]
        return diameter, space, area, as_per_cm
    
    def getStirrupsInfo(self):
        x_array, shear_area_per_cm = self.x, self.shear_area_per_cm
        s_max = self.s_max
        x = self.concrete_beam.x_begin
        transversal_steel = fconcrete.TransvSteelBars()

        while x<self.concrete_beam.x_end:
            x_loop = ((x_array>x) & (x_array<x+s_max))
            shear = max(abs(shear_area_per_cm[x_loop]))
            diameter, space, area, as_per_cm = self.getComercialInfo(shear)
            single_beam_element = self.concrete_beam.getSingleBeamElementInX(x)[1]
            height = single_beam_element.section.height
            width = single_beam_element.section.width()
            c = single_beam_element.section.material.c
            transversal_steel.add(
                fconcrete.TransvSteelBar(x, height-2*c, width-2*c, diameter, space, area, as_per_cm)
            )
            x += space
            
        return transversal_steel