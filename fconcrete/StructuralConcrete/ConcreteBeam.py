from fconcrete.Structural.Beam import Beam
from fconcrete.StructuralConcrete import AvailableLongConcreteSteelBar, AvailableTransvConcreteSteelBar
import fconcrete as fc
import numpy as np
import warnings

class ConcreteBeam(Beam):

    def __init__(self, loads, beam_elements,
                 bar_steel_removal_step=2, bar_steel_max_removal=100, design_factor=1.4, division=1000,
                 maximum_displacement=1/250,
                 transversal_bar_inclination_angle=90,
                 tilt_angle_of_compression_struts=45,
                 transversal_bar_fyk=50,
                 available_long_steel_bars=AvailableLongConcreteSteelBar(),
                 available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
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

                >>>    beam_element1 = fc.BeamElement([n1, n2], section)
                >>>    beam_element2 = fc.BeamElement([n2, n3], section)
                >>>    beam_element3 = fc.BeamElement([n3, n4], section)

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
        self.checkInput()
        Beam.__init__(self, loads, beam_elements, **options)
        
        
        self.bar_steel_removal_step = bar_steel_removal_step
        self.bar_steel_max_removal = bar_steel_max_removal
        self.design_factor = design_factor
        self.division = division
        self.maximum_displacement = maximum_displacement
        self.transversal_bar_inclination_angle = transversal_bar_inclination_angle
        self.tilt_angle_of_compression_struts = tilt_angle_of_compression_struts
        self.transversal_bar_fyk = transversal_bar_fyk
        self.available_long_steel_bars = available_long_steel_bars
        self.available_transv_steel_bars = available_transv_steel_bars
        
        if options.get("solve_ELS") != False:
            self.solve_ELS()
        
        if options.get("solve_transv_steel") != False:
            self.transv_steel_bars_solution_info = fc.TransvSteelBarSolve(concrete_beam=self,
                                                                                 fyk=transversal_bar_fyk,
                                                                                 theta_in_degree=tilt_angle_of_compression_struts,
                                                                                 alpha_in_degree = transversal_bar_inclination_angle)
            self.transv_steel_bars = self.transv_steel_bars_solution_info.steel_bars
            
        if options.get("solve_long_steel") != False:
            self.long_steel_bars_solution_info = fc.LongSteelBarSolve(concrete_beam=self)
            self.long_steel_bars = self.long_steel_bars_solution_info.steel_bars
            
    
    def solve_ELS(self):
        for beam_element in self.initial_beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            x, y = self.getDisplacementDiagram(x_begin=x_begin, x_end=x_end, division=200)
            if max(abs(y)) > beam_element.length*self.maximum_displacement:
                raise Exception("Displacement too big between x={}cm and x={}cm".format(x_begin, x_end))
    
    def getShearDesignDiagram(self, **options_diagram):
        x, shear_diagram = self.getShearDiagram(division=self.division)
        return x, self.design_factor*shear_diagram
    
    @staticmethod
    def checkInput():
        pass
        #if (decalaged_length_method not in ["full", "simplified"]): raise Exception("Decalage Method available are 'full' or 'simplified")