from fconcrete.Structural.Beam import Beam
from fconcrete.StructuralConcrete import AvailableLongConcreteSteelBar, AvailableTransvConcreteSteelBar, AvailableConcrete
from fconcrete.Structural.BeamElement import BeamElement, BeamElements
from fconcrete.helpers import timeit
import fconcrete as fc
import numpy as np
import warnings
import matplotlib.pyplot as plt
import time
from fconcrete.StructuralConcrete.AvailableMaterials import solve_cost

class ConcreteBeam(Beam):
    """
    Beam associated with the material concrete.
    
    Attributes
    ----------
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
    """
    def __init__(self,
                 loads,
                 beam_elements=None,
                 nodes=None,
                 section=None,
                 design_factor=1.4,
                 division=1000,
                 maximum_displacement_allowed=lambda beam_element_length : beam_element_length/250,
                 available_long_steel_bars=AvailableLongConcreteSteelBar([8]),
                 bar_steel_removal_step=2,
                 bar_steel_max_removal=100,
                 available_transv_steel_bars=AvailableTransvConcreteSteelBar([8]),
                 transversal_bar_inclination_angle=90,
                 tilt_angle_of_compression_struts=45,
                 transversal_bar_fyk=50,
                 available_concrete=AvailableConcrete(),
                 time_begin_long_duration=0,
                 lifetime_structure=70,
                 biggest_aggregate_dimension=1.5,
                 verbose = False,
                 **options):
        """
            Returns a concrete_beam element.
            
                Call signatures:

                    ConcreteBeam(loads,
                                beam_elements=None,
                                nodes=None,
                                section=None,
                                bar_steel_removal_step=2,
                                bar_steel_max_removal=100,
                                design_factor=1.4,
                                division=1000,
                                maximum_displacement_allowed=lambda beam_element_length : beam_element_length/250,
                                transversal_bar_inclination_angle=90,
                                tilt_angle_of_compression_struts=45,
                                transversal_bar_fyk=50,
                                available_long_steel_bars=AvailableLongConcreteSteelBar(),
                                available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
                                available_concrete=AvailableConcrete(),
                                time_begin_long_duration=0,
                                lifetime_structure=70,
                                biggest_aggregate_dimension=1.5,
                                verbose = False,
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
            loads: [Load]
                Define the loads supported for the beam.
            
            beam_elements: [BeamElement], optional
                Define the beam_elements that, together, makes the whole Beam. 
                Optional if nodes and section is given.
            
            nodes: [Node]
                Define the nodes that are going to make the whole Beam.
                Not used if beam_elements is given.
                
            section: Section
                Define the section that are going to make the whole Beam.
                Not used if beam_elements is given.
            
            design_factor: float, optional
                Define the number that is going to be multiplied to de momentum diagram and shear diagram.
                If your load is already a design load, you should set design_factor=1.
                Default value is 1.4.
                
            division: int, optional
                Define the number of division solutions for the beam.
                The beam will be divided in equally spaced points and all results (displacement, momentum, shear) will be calculated to these points.
                Default value is 1.4.
            
            maximum_displacement_allowed: float, optional
                For each beam element, compare its maximum displacement with maximum_displacement_allowed(beam_element_length).
                This is used to solve the ELS shown in NBR 6118.
                If a beam_element length is 120cm, its maximum displacement is 1cm and maximum_displacement_allowed is 120/250=0.45cm < 1cm. Therefore, in this condition, the ELS step will raise an error.
                Default value is lambda beam_element_length : beam_element_length/250.
                
            available_long_steel_bars: AvailableLongConcreteSteelBar, optional
                Define the available longitudinal steel bars. 
                You can set the available diameters, cost_by_meter, fyw, E, etc.
                See more information in fc.AvailableLongConcreteSteelBar docstring.
                Default AvailableLongConcreteSteelBar([8]).
                
            bar_steel_removal_step: int, optional
                Define the step during the removal of the bar. Instead of taking the steel bars one by one, the bar_steel_removal_step will make the removal less constant.
                I makes the building process easier. 
                Default value is 2.
                
            bar_steel_max_removal: int, optional
                Define the max times it is possible to remove the bar.
                Default value is 100.
                
            time_begin_long_duration: float, optional
                The time, in months, relative to the date of application of the long-term load
                Default value is 0.
            
            lifetime_structure: float, optional
                The time, in months, when the value of the deferred arrow is desired;
                Default value is 70.
            
            biggest_aggregate_dimension: float, optional
                Maximum dimension characteristic of the biggest aggregate, in cm.
                Default value is 1.5.
                
            verbose: bool, optional
                Print the the steps and their durations.
                Default value is False.
            
        """
        start = time.time()
        
        beam_elements = self._checkInput(
            nodes=nodes,
            beam_elements=beam_elements,
            material=available_concrete.material,
            section=section
        )
        
        
        timeit(verbose, "Solve structural beam")(Beam.__init__(self, loads, beam_elements, solve_displacement=False, **options))
        
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
        self.available_concrete = available_concrete
        self.time_begin_long_duration = time_begin_long_duration
        self.lifetime_structure = lifetime_structure
        self.biggest_aggregate_dimension = biggest_aggregate_dimension
        self.verbose = verbose
            
        if options.get("solve_transv_steel") != False:
            timeit(verbose, "Solve transv steel")(self.solve_transv_steel)()
            
        if options.get("solve_long_steel") != False:
            self.solve_long_steel()
        
        if options.get("solve_ELS") != False:
            timeit(verbose, "Solve ELS")(self.solve_ELS)()
        
        if options.get("solve_cost") != False:
            self.cost, self.cost_table, self.subtotal_table = solve_cost(self)
        
        end = time.time()
        self.processing_time = end-start
    
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
        self.initial_beam_elements = self._toConcreteBeamElements(self.initial_beam_elements)
        self.solve_displacement_constants()
        for beam_element in self.initial_beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            _, y = self.getConcreteDisplacementDiagram(x_begin=x_begin, x_end=x_end, division=200)
            max_disp = self.maximum_displacement_allowed(beam_element.length)
            if max(abs(y)) > max_disp:
                raise Exception("Displacement too big between x={}cm and x={}cm. Maximum allowed is {}cm, but the beam lement reached {}cm".format(
                    x_begin, x_end, max_disp, max(abs(y))))
    
    def getShearDesignDiagram(self, **options_diagram):
        x, shear_diagram = self.getShearDiagram(division=self.division)
        return x, self.design_factor*shear_diagram
        
    def plotTransversalInX(self, x):
        positive_bars, negative_bars = self.long_steel_bars.getPositiveandNegativeLongSteelBarsInX(x=x)
        transversal_bar = self.transv_steel_bars.getTransversalBarAfterX(x)
        
        _, beam_element = self.getBeamElementInX(x)
        material, section = beam_element.material, beam_element.section
        
        fig, ax = section.plot()
        fig, ax = transversal_bar.plot(fig=fig, ax=ax, c=material.c)
        fig, ax = positive_bars.plotTransversal(self, x, fig=fig, ax=ax)
        fig, ax = negative_bars.plotTransversal(self, x, fig=fig, ax=ax)

    def solve_transv_steel(self):
        self.transv_steel_bars_solution_info = fc.TransvSteelBarSolve(concrete_beam=self,
                                                                        fyk=self.transversal_bar_fyk,
                                                                        theta_in_degree= self.tilt_angle_of_compression_struts,
                                                                        alpha_in_degree = self.transversal_bar_inclination_angle)
        self.transv_steel_bars = self.transv_steel_bars_solution_info.steel_bars
    
    def solve_long_steel(self):
        self.long_steel_bars_solution_info = fc.LongSteelBarSolve(concrete_beam=self)
        self.long_steel_bars = self.long_steel_bars_solution_info.steel_bars
    
    @staticmethod
    def _checkInput(**inputs):
        nodes, beam_elements, section, material = inputs.get("nodes"), inputs.get("beam_elements"), inputs.get("section"), inputs.get("material")
        if nodes and section:
            section.d = 0.8*section.height
            if len(nodes) == 1: raise Exception("Must contain at least 2 nodes to create a beam")
            beam_elements = []
            for i in range(0,len(nodes)-1):
                beam_elements = [*beam_elements, fc.BeamElement([nodes[i], nodes[i+1]], section, material)]
            return beam_elements
        elif beam_elements and section:
            beam_elements = BeamElements.create(beam_elements)
            beam_elements = beam_elements.changeProperty("material", lambda x:material)
            section.d = 0.8*section.height
            return beam_elements.changeProperty("section", lambda x:section)
        elif beam_elements:
            beam_elements_modified = []
            for beam_element in beam_elements:
                beam_element.section.d = 0.8*beam_element.section.height
                beam_elements_modified = [*beam_elements_modified, beam_element]
            return beam_elements_modified
        
        return beam_elements
        #if (decalaged_length_method not in ["full", "simplified"]): raise Exception("Decalage Method available are 'full' or 'simplified")
    
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
            is_in_the_beam_element = (self.long_steel_bars_solution_info.x >= x_begin) &  (self.long_steel_bars_solution_info.x <= x_end)
            positive_area_info = self.long_steel_bars_solution_info.positive_areas_info[:, is_in_the_beam_element]
            negative_area_info = self.long_steel_bars_solution_info.negative_areas_info[:, is_in_the_beam_element]

            positive_area_diagram = positive_area_info[2]
            negative_area_diagram = negative_area_info[2]
            positive_area_diagram = positive_area_diagram[~np.isnan(positive_area_diagram)]
            negative_area_diagram = negative_area_diagram[~np.isnan(negative_area_diagram)]
            
            max_positive_area = abs(positive_area_diagram).max(initial=0)
            max_negative_area = abs(negative_area_diagram).max(initial=0)
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
    
    def __name__(self):
        return "ConcreteBeam"