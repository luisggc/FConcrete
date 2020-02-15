import numpy as np
from .TransvSteelBar import TransvSteelBar, TransvSteelBars
from math import radians, sin, tan

class TransvSteelBarSolve():
    def __init__(self, concrete_beam, fyk=50, theta_in_degree=45, alpha_in_degree = 90):
        self.available = concrete_beam.available_transv_steel_bars
        self.concrete_beam = concrete_beam
        x, shear_diagram = concrete_beam.getShearDesignDiagram(division=concrete_beam.division)
        self.x = x
        self.shear_diagram = abs(shear_diagram)
        self.fyk = fyk
        self.fyd = fyk/1.4
        self.theta = radians(theta_in_degree)
        self.alpha = radians(alpha_in_degree)
        v_rd2, d, v_sd = self.checkProbableCompressedConnectingRod()
        self.s_max = self._getS_max(v_rd2, d, v_sd, self.available)
        _, self.shear_area_per_cm = self.getShearSteelAreaPerCmDiagram()
        self.steel_bars = self.getStirrupsInfo()
    
    @staticmethod
    def _getS_max(v_rd2, d, v_sd, available):
        s_max = min(0.6*d, 30) if v_sd <= 0.67*v_rd2 else min(0.3*d, 20)        
        return s_max
        
    def checkProbableCompressedConnectingRod(self):
        """
            Check probable compressed connecting rod.
            It is probable because checks only where the shear is maximum.

                Call signatures:

                    concrete_beam.transv_steel_bars_solution_info.checkProbableCompressedConnectingRod()

            Returns
            -------
            v_rd2 : number
                Shear of calculation, related to the ruin of compressed concrete diagonals in kN.
                
            d : number
                Distance from longitudinal steel bars to the other extremity of the section in cm.
            
            max_shear : number
                Maximum shear in kN.
        """
        max_shear = max(self.shear_diagram)
        max_shear_x = self.x[self.shear_diagram == max_shear][0]
        _, single_beam_element = self.concrete_beam.getBeamElementInX(max_shear_x)
        v_rd2 = self.getV_rd2(single_beam_element)
        check = max_shear <= v_rd2
        if check == False: raise Exception("Shear ({}kN) in x={} is greater or equal to maximum shear allowed ({}kN)".format(max_shear, max_shear_x, v_rd2))
        d = single_beam_element.section.minimum_steel_height
        
        return v_rd2, d, max_shear
    
    def getV_rd2(self, single_beam_element):
        """
            Giving a beam element, calculates the shear related to the ruin of compressed concrete diagonals in kN.
        """
        fck = single_beam_element.material.fck
        bw = single_beam_element.section.bw
        d = single_beam_element.section.minimum_steel_height
        
        fcd = single_beam_element.material.fcd
        alpha_v2 = (1-fck/25)
        v_rd2 = 0.54*alpha_v2*fcd*bw*d*(sin(self.theta))*(tan(self.alpha)**(-1)+tan(self.theta)**(-1))
        return v_rd2
    
    def getMinimumSteelAreaPerCm(self,single_beam_element):
        """
            Giving a beam element, calculates the minimum steel area (cmˆ2) per cm.
        """
        fctm = single_beam_element.material.fctm
        bw = single_beam_element.section.bw
        As_per_cm_min = 0.2*fctm*bw*sin(self.alpha)/self.fyk
        return As_per_cm_min
    

    def getShearSteelAreaPerCm(self, x, v_sd): 
        """
            Calculates the shear steel area (cmˆ2) per cm considering the restrictions.
        """
        # can be optimized
        _, single_beam_element = self.concrete_beam.getBeamElementInX(x)
        v_rd2 = self.getV_rd2(single_beam_element)
        As_per_cm_min = self.getMinimumSteelAreaPerCm(single_beam_element)
        
        _, single_beam_element = self.concrete_beam.getBeamElementInX(x)
        bw = single_beam_element.section.bw
        d = single_beam_element.section.minimum_steel_height
        fctd = single_beam_element.material.fctd

        v_c0 = 0.6*fctd*bw*d
        v_c1 = np.interp(v_sd, [v_c0, v_c0, v_rd2], [v_c0, v_c0, 0])
        v_c = v_c1
        v_sw = max(v_sd - v_c, 0)
        
        As_per_cm = v_sw/(0.9*d*self.fyd*(sin(self.alpha))*(tan(self.alpha)**(-1)+tan(self.theta)**(-1)))
        
        return max(As_per_cm, As_per_cm_min)

    def getShearSteelAreaPerCmDiagram(self):
        """
            Apply concrete_beam.transv_steel_bars_solution_info.getShearSteelAreaPerCm for parts of the concrete_beam.
            
            Returns
            -------
            x : list of number
                The x position of the division in cm
            
            y : list of number
                The value of shear area per cm for each x.
        """
        shear_area_per_cm = [self.getShearSteelAreaPerCm(x_u, v_sd) for x_u, v_sd in zip(self.x, self.shear_diagram)]
        return self.x, np.array(shear_area_per_cm)
    
    def getComercialInfo(self, as_per_cm):
        """
            Get comercial info giving the area per cm.
            
            Returns
            -------
            diameter : number
                Diameter in cm.
            
            space : number
                Longitudinal space between the transversal steel.
                
            area : number
                Area of the transversal steel bar in cmˆ2.
                
            as_per_cm : number
                Area of the transversal steel bar in cmˆ2 per cm.
        """
        table = self.available.table
        comercial_info = table[table[:, 3] >= as_per_cm]
        if len(comercial_info) == 0 : raise Exception("It is not possible to place the transversal steel bar using the provided space_in_multiple_of or diameter argument. When you create the concrete_beam, you should change the argument 'available_transv_steel_bars = fc.AvailableTransvConcreteSteelBar(diameters=[x], space_is_multiple_of=[y])' giving y a smaller number or diameter a bigger one.")
        diameter, space, area, as_per_cm = comercial_info[0]
        return diameter, space, area, as_per_cm
    
    def getStirrupsInfo(self):
        """
            Format all informations and return a TransvSteelBars instance.
        """
        x_array, shear_area_per_cm = self.x, self.shear_area_per_cm
        s_max = self.s_max
        x = self.concrete_beam.x_begin
        transversal_steel = TransvSteelBars()

        while x<self.concrete_beam.x_end:
            x_loop = ((x_array>x) & (x_array<x+s_max))
            shear = max(abs(shear_area_per_cm[x_loop]))
            diameter, space, area, as_per_cm = self.getComercialInfo(shear)
            single_beam_element = self.concrete_beam.getBeamElementInX(x)[1]
            height = single_beam_element.section.height
            width = single_beam_element.section.width()
            c = single_beam_element.material.c
            anchor = max(5*diameter, 5)
            length = width*2+height*2+anchor
            cost = length*self.available.cost_by_meter[diameter*10]/100
            
            transversal_steel.add(
                TransvSteelBar(
                    x=x,
                    height=height-2*c,
                    width=width-2*c,
                    diameter=diameter,
                    space_after=space,
                    area=area,
                    as_per_cm=as_per_cm,
                    anchor = anchor,
                    length=length,
                    cost=cost)
            )
            x += space
        
        # Add by the end of the beam
        transversal_steel.add(
                TransvSteelBar(
                    x=self.concrete_beam.x_end,
                    height=height-2*c,
                    width=width-2*c,
                    diameter=diameter,
                    space_after=space,
                    area=area,
                    as_per_cm=as_per_cm,
                    anchor = anchor,
                    length=length,
                    cost=cost)
        )
        
        return transversal_steel