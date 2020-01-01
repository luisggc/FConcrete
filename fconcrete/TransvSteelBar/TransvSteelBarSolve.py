import numpy as np
import fconcrete
from math import pi, sin, tan

class TransvSteelBarSolve():
    def __init__(self, concrete_beam, fyk=50, theta_in_degree=45, alpha_in_degree = 90):
        self.available = fconcrete.config.available_material["concrete_transv_steel_bars"]
        self.concrete_beam = concrete_beam
        x, shear_diagram = concrete_beam.getShearDesignDiagram(division=concrete_beam.division)
        self.x = x
        self.shear_diagram = abs(shear_diagram)
        self.fyk = fyk
        self.fyd = fyk/1.4
        self.theta = (theta_in_degree*pi)/180
        self.alpha = (alpha_in_degree*pi)/180
        v_rd2, d, v_sd = self.checkProbableCompressedConnectingRod()
        self.s_max = self._getS_max(v_rd2, d, v_sd, self.available)
        self.shear_area_per_cm = self.getShearSteelAreaPerCmDiagram()
        self.steel_bars = self.getStirrupsInfo()
    
    @staticmethod
    def _getS_max(v_rd2, d, v_sd, available):
        s_max = min(0.6*d, 30) if v_sd <= 0.67*v_rd2 else min(0.3*d, 20)        
        return s_max
        
    def checkProbableCompressedConnectingRod(self):
        max_shear = max(self.shear_diagram)
        max_shear_x = self.x[self.shear_diagram == max_shear][0]
        _, single_beam_element = self.concrete_beam.getSingleBeamElementInX(max_shear_x)
        v_rd2 = self.getV_rd2(single_beam_element)
        check = max_shear <= v_rd2
        if check == False: raise Exception("Shear ({}kN) in x={} is greater or equal to maximum shear allowed ({}kN)".format(max_shear, max_shear_x, v_rd2))
        return v_rd2, single_beam_element.section.d, max_shear
    
    def getV_rd2(self, single_beam_element):
        fck = single_beam_element.material.fck
        bw = single_beam_element.section.bw
        d = single_beam_element.section.d
        fcd = single_beam_element.material.fcd
        alpha_v2 = (1-fck/25)
        v_rd2 = 0.54*alpha_v2*fcd*bw*d*(sin(self.theta))*(tan(self.alpha)**(-1)+tan(self.theta)**(-1))
        return v_rd2
    
    def getMinimumSteelAreaPerCm(self,single_beam_element):
        fctm = single_beam_element.material.fctm
        bw = single_beam_element.section.bw
        As_per_cm_min = 0.2*fctm*bw*sin(self.alpha)/self.fyk
        return As_per_cm_min
    

    def getShearSteelAreaPerCm(self, x, v_sd): 
        # can be optimized
        _, single_beam_element = self.concrete_beam.getSingleBeamElementInX(x)
        v_rd2 = self.getV_rd2(single_beam_element)
        As_per_cm_min = self.getMinimumSteelAreaPerCm(single_beam_element)
        
        _, single_beam_element = self.concrete_beam.getSingleBeamElementInX(x)
        bw = single_beam_element.section.bw
        d = single_beam_element.section.d
        fctd = single_beam_element.material.fctd

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
            c = single_beam_element.material.c
            transversal_steel.add(
                fconcrete.TransvSteelBar(x, height-2*c, width-2*c, diameter, space, area, as_per_cm)
            )
            x += space
            
        return transversal_steel