from fconcrete.Structural.Beam import Beam
from fconcrete.StructuralConcrete import AvailableLongConcreteSteelBar, AvailableTransvConcreteSteelBar
import fconcrete as fc
import numpy as np
import warnings
import matplotlib.pyplot as plt

class ConcreteBeam(Beam):

    def __init__(self,
                 loads,
                 beam_elements,
                 bar_steel_removal_step=2,
                 bar_steel_max_removal=100,
                 design_factor=1.4,
                 division=1000,
                 maximum_displacement_allowed=1/250,
                 transversal_bar_inclination_angle=90,
                 tilt_angle_of_compression_struts=45,
                 transversal_bar_fyk=50,
                 available_long_steel_bars=AvailableLongConcreteSteelBar(),
                 available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
                 time_begin_long_duration=0,
                 lifetime_structure=70,
                 biggest_aggregate_dimension=1.5,
                 **options):
        """
            Returns a concrete_beam element.
            
                Call signatures::

                    ConcreteBeam(loads,
                                beam_elements,
                                bar_steel_removal_step=2,
                                bar_steel_max_removal=100,
                                design_factor=1.4,
                                division=1000,
                                maximum_displacement_allowed=1/250,
                                transversal_bar_inclination_angle=90,
                                tilt_angle_of_compression_struts=45,
                                transversal_bar_fyk=50,
                                available_long_steel_bars=AvailableLongConcreteSteelBar(),
                                available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
                                time_begin_long_duration=0,
                                lifetime_structure=70,
                                **options)

                >>>    material = fc.Concrete(fck='20 MPa', aggressiveness=2)
                >>>    section = fc.Rectangle(25,56, material)

                >>>    f1 = fc.Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
                >>>    f2 = fc.Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
                >>>    f3 = fc.Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

                >>>    n1 = fc.Node.SimpleSupport(x=0)
                >>>    n2 = fc.Node.SimpleSupport(x=113)
                >>>    n3 = fc.Node.SimpleSupport(x=583)
                >>>    n4 = fc.Node.SimpleSupport(x=1188)

                >>>    beam_element1 = fc.BeamElement([n1, n2], section)
                >>>    beam_element2 = fc.BeamElement([n2, n3], section)
                >>>    beam_element3 = fc.BeamElement([n3, n4], section)

                >>>    fc.ConcreteBeam(
                        loads = [f1, f2, f3],
                        beam_elements = [beam_element1, beam_element2, beam_element3],
                        bar_steel_max_removal = 2
                    )
            
            Parameters
            ----------
            loads : [Load]
                Define the loads supported for the beam.
            
            beam_elements : [BeamElement]
                Define the beam_elements that, together, makes the whole Beam. 
            
            maximum_displacement_allowed: float, optional (default 1/250)
                For each beam element, compare its maximum displacement with beam_element.length*maximum_displacement_allowed.
                This is used to solve the ELS shown in NBR 6118.
                If a beam_element length is 120cm, its maximum displacement is 1cm and maximum_displacement_allowed is 1/250, 120*(1/250)=0.45cm < 1cm. Therefore, in this condition, the ELS with raise a error.
            
            bar_steel_removal_step: int, optional (default 2)
                Define the step during the removal of the bar. Instead of taking the steel bars one by one, the bar_steel_removal_step will make the removal less constant.
                I makes the building process easier. 
                
            bar_steel_max_removal: int, optional (default 100)
                Define the max times it is possible to remove the bar.
            
            time_begin_long_duration: float, optional (default 0)
                The time, in months, relative to the date of application of the long-term load
            
            lifetime_structure: float, optional (default 70)
                The time, in months, when the value of the deferred arrow is desired;
            
            biggest_aggregate_dimension: float, optional (default 1.5)
                Maximum dimension characteristic of the biggest aggregate, in cm.
                
            
        """
        self.checkInput()
        Beam.__init__(self, loads, beam_elements, solve_displacement=False, **options)
        
        self.bar_steel_removal_step = bar_steel_removal_step
        self.bar_steel_max_removal = bar_steel_max_removal
        self.design_factor = design_factor
        self.division = division
        self.maximum_displacement_allowed = maximum_displacement_allowed
        self.transversal_bar_inclination_angle = transversal_bar_inclination_angle
        self.tilt_angle_of_compression_struts = tilt_angle_of_compression_struts
        self.transversal_bar_fyk = transversal_bar_fyk
        self.available_long_steel_bars = available_long_steel_bars
        self.available_transv_steel_bars = available_transv_steel_bars
        self.time_begin_long_duration = time_begin_long_duration
        self.lifetime_structure = lifetime_structure
        self.biggest_aggregate_dimension = biggest_aggregate_dimension
        
        if options.get("solve_transv_steel") != False:
            self.transv_steel_bars_solution_info = fc.TransvSteelBarSolve(concrete_beam=self,
                                                                                 fyk=transversal_bar_fyk,
                                                                                 theta_in_degree=tilt_angle_of_compression_struts,
                                                                                 alpha_in_degree = transversal_bar_inclination_angle)
            self.transv_steel_bars = self.transv_steel_bars_solution_info.steel_bars
            
        if options.get("solve_long_steel") != False:
            self.long_steel_bars_solution_info = fc.LongSteelBarSolve(concrete_beam=self)
            self.long_steel_bars = self.long_steel_bars_solution_info.steel_bars
        
        if options.get("solve_ELS") != False:
            self.initial_beam_elements = self._toConcreteBeamElements(self.initial_beam_elements)
            self.solve_displacement_constants()
            self.solve_ELS()
    
    def getConcreteDisplacementDiagram(self, **options):
        x, y = self.getDisplacementDiagram(**options)
        return x, y*(self._time_function_coefficient(self.lifetime_structure)-self._time_function_coefficient(self.time_begin_long_duration))
    
    def plotConcreteDisplacementDiagram(self, **options):
        x, y = self.getConcreteDisplacementDiagram(**options)
        plt.plot(x, y)
            
    @staticmethod
    def _time_function_coefficient(t):
        if t>70: return 2
        return 0.68*(0.996**t)*t**0.32 
    
    def solve_ELS(self):
        for beam_element in self.initial_beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            x, y = self.getConcreteDisplacementDiagram(x_begin=x_begin, x_end=x_end, division=200)
            if max(abs(y)) > beam_element.length*self.maximum_displacement_allowed:
                raise Exception("Displacement too big between x={}cm and x={}cm. Maximum allowed is {}cm, but the beam lement reached {}cm".format(
                    x_begin, x_end, beam_element.length*self.maximum_displacement_allowed, max(abs(y))))
    
    def getShearDesignDiagram(self, **options_diagram):
        x, shear_diagram = self.getShearDiagram(division=self.division)
        return x, self.design_factor*shear_diagram
    
    def _toConcreteBeamElements(self, beam_elements):
        for beam_element in beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            section = beam_element.section
            material = beam_element.material
            
            I = section.I
            y_cg = section.y_cg
            bw = section.bw
            d = section.d
            h = section.height
            
            fctm = material.fctm
            E_cs = material.E_cs
            E_s = self.available_long_steel_bars.E
            
            _, positive_area_info, negative_area_info = self.long_steel_bars_solution_info.getComercialSteelAreaDiagram(x_begin=x_begin, x_end=x_end, division=200)
            positive_area_diagram = positive_area_info[2]
            negative_area_diagram = negative_area_info[2]
            positive_area_diagram = positive_area_diagram[~np.isnan(positive_area_diagram)]
            negative_area_diagram = negative_area_diagram[~np.isnan(negative_area_diagram)]
            
            max_positive_area = max(abs(positive_area_diagram))
            max_negative_area = max(abs(negative_area_diagram))
            max_area = max(max_positive_area, max_negative_area)
            
            # fator que correlaciona aproximadamente a resistência à tração na flexão com a resistência à tração direta
            y_t = y_cg if max_area==max_positive_area else h-y_cg
            alpha = 1.5
            M_r = alpha*fctm*I/y_t
            _, momentum_diagram = self.getMomentumDiagram(x_begin=x_begin, x_end=x_end, division=200)
            M_a = self.design_factor*max(abs(momentum_diagram))
            
            mra3 = (M_r/M_a)**3
            alpha_e = E_s/E_cs
            
            a1, a2, a3 = bw/2, max_area*alpha_e, -max_area*alpha_e*d
            x2 = (-a2+(a2**2-4*a1*a3)**0.5)/(2*a1)
            I2 = bw*x2**3/3+a2*(x2-d)**2
            
            new_I = min((mra3*I+(1-mra3)*I2),I)
            beam_element.I = new_I
            beam_element.flexural_rigidity = E_cs * new_I
            
        return beam_elements
        
    @staticmethod
    def checkInput():
        pass
        #if (decalaged_length_method not in ["full", "simplified"]): raise Exception("Decalage Method available are 'full' or 'simplified")