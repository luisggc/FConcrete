from fconcrete.Structural.Beam import Beam
from fconcrete.StructuralConcrete import AvailableLongConcreteSteelBar, AvailableTransvConcreteSteelBar, AvailableConcrete
from fconcrete.Structural.BeamElement import BeamElement, BeamElements
from fconcrete.helpers import timeit
import fconcrete as fc
import numpy as np
import matplotlib.pyplot as plt
import time
from fconcrete.StructuralConcrete.AvailableMaterials import solve_cost

class ConcreteBeam(Beam):
    """
        Beam associated with the material concrete.
        All attbributes from :doc:`Beam Class <../fconcrete.Structural.Beam>` can be used.
        
        Attributes
        ----------
        available_concrete : AvailableConcrete
            Same constant from input.
            Define the available concrete. 
            You can set the available fck, cost_by_m3, aggressiveness and aggregate.
            See more information in fc.AvailableConcrete docstring or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
            Default AvailableConcrete() which means:
            
            - 30 MPa;
            - R$353.30 by meterˆ3;
            - The aggressiveness is 3;
            - Aggregate is granite;
            - Biggest aggregate dimension is 1.5cm.
            
        available_long_steel_bars : AvailableLongConcreteSteelBar
            Same constant from input.
            Define the available longitudinal steel bars. 
            You can set the available diameters, cost_by_meter, fyw, E, etc.
            See more information in fc.AvailableLongConcreteSteelBar docstring  or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
            Default AvailableLongConcreteSteelBar([8]) which means:
            
            - 8mm diameter;
            - 0.5cmˆ2 area;
            - R$2.0575 by meter cost;
            - fyw equal to 50kN/cmˆ2;
            - Young Modulus (E) is 21000kN/cmˆ2;
            - Max number of steel in the section is 200;
            - Surface type is ribbed.
                
        available_transv_steel_bars : AvailableLongConcreteSteelBar
            Same constant from input.
            Define the available longitudinal steel bars. 
            You can set the available diameters, cost_by_meter, fyw, E, etc.
            See more information in fc.AvailableLongConcreteSteelBar docstring or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
            Default AvailableLongConcreteSteelBar([8]) which means:
            
            - 8mm diameter;
            - 0.5cmˆ2 area;
            - R$2.0575 by meter cost;
            - The longitudinal space between transversal steel are multiple of 5;
            - fyw equal to 50kN/cmˆ2;
            - Transversal bar inclination angle of 90 degrees;
            - Tilt angle of compression struts of 45 degrees.
        
        bar_steel_max_removal : int
            Same constant from input.
            Define the max times it is possible to remove the bar.
            Default value is 100.
        
        bar_steel_removal_step : int
            Same constant from input.
            Define the step during the removal of the bar. Instead of taking the steel bars one by one, the bar_steel_removal_step will make the removal less constant.
            I makes the building process easier. 
            Default value is 2.
            
        cost : number
            Total material cost of the beam.

        cost_table : number
            Detailed table with all materials and their costs.

        design_factor : number
            Same constant from input.
            Define the number that is going to be multiplied to de momentum diagram and shear diagram.
            If your load is already a design load, you should set design_factor=1.
            Default value is 1.4.

        division : int
            Same constant from input.
            Define the number of division solutions for the beam.
            The beam will be divided in equally spaced points and all results (displacement, momentum, shear) will be calculated to these points.
            Default value is 1.4.
            
        lifetime_structure : number
            The time, in months, when the value of the deferred arrow is desired;
            Default value is 70.
                
        long_steel_bars : LongSteelBars
            Longitudinal steels used in the beam.

        long_steel_bars_solution_info : LongSteelBarSolve
            Information about the solution for longitudinal steels used in the beam.
            More information in the :doc:`LongSteelBarSolve Class <../fconcrete.StructuralConcrete.LongSteelBar.LongSteelBarSolve>` documentation.

        maximum_displacement_allowed : number
            Same constant from input.
            For each beam element, compare its maximum displacement with maximum_displacement_allowed(beam_element_length).
            This is used to solve the ELS shown in NBR 6118.
            If a beam_element length is 120cm, its maximum displacement is 1cm and maximum_displacement_allowed is 120/250=0.45cm < 1cm. Therefore, in this condition, the ELS step will raise an error.
            Default value is lambda beam_element_length : beam_element_length/250.

        processing_time : number
            Time for resolution of the concrete beam.

        subtotal_table : number
            Table with each type of material and their costs.

        tilt_angle_of_compression_struts : number
            Same constant from input.
            Tilt angle of compression struts in degrees.
            Default 45 degrees.
                
        time_begin_long_duration : number
            The time, in months, relative to the date of application of the long-term load
            Default value is 0.
                
        transv_steel_bars : TransvSteelBar
            Transversal steels used in the beam.

        transv_steel_bars_solution_info : TransvSteelBarSolve
            Information about the solution for transversal steels used in the beam.
            More information in the :doc:`TransvSteelBarSolve Class <../fconcrete.StructuralConcrete.TransvSteelBar.TransvSteelBarSolve>` documentation.

        verbose : `bool`
            Print the the steps and their durations.
            Default value is False.
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
                 tilt_angle_of_compression_struts=45,
                 available_concrete=AvailableConcrete(),
                 time_begin_long_duration=0,
                 lifetime_structure=70,
                 verbose = False,
                 **options):
        """
            Returns a concrete_beam element.
            
                Call signatures:

                    `ConcreteBeam(loads,
                                beam_elements=None,
                                nodes=None,
                                section=None,
                                bar_steel_removal_step=2,
                                bar_steel_max_removal=100,
                                design_factor=1.4,
                                division=1000,
                                maximum_displacement_allowed=lambda beam_element_length : beam_element_length/250,
                                tilt_angle_of_compression_struts=45,
                                available_long_steel_bars=AvailableLongConcreteSteelBar(),
                                available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
                                available_concrete=AvailableConcrete(),
                                time_begin_long_duration=0,
                                lifetime_structure=70,
                                verbose = False,
                                **options)`

                >>> n1 = fc.Node.SimpleSupport(x=0, length=20)
                >>> n2 = fc.Node.SimpleSupport(x=400, length=20)
                >>> f1 = fc.Load.UniformDistributedLoad(-0.000001, x_begin=0, x_end=1)
                 
                >>> concrete_beam = fc.ConcreteBeam(
                >>>     loads = [f1],
                >>>     nodes = [n1, n2],
                >>>     section = fc.Rectangle(20,1000),
                >>>     division = 20
                >>> )
            
            Parameters
            ----------
            loads : [Load]
                Define the loads supported for the beam.
            
            beam_elements : [BeamElement], optional
                Define the beam_elements that, together, makes the whole Beam. 
                Optional if nodes and section is given.
            
            nodes : [Node]
                Define the nodes that are going to make the whole Beam.
                Not used if beam_elements is given.
                
            section : Section
                Define the section that are going to make the whole Beam.
                Not used if beam_elements is given.
            
            design_factor : number, optional
                Define the number that is going to be multiplied to de momentum diagram and shear diagram.
                If your load is already a design load, you should set design_factor=1.
                Default value is 1.4.
                
            division : int, optional
                Define the number of division solutions for the beam.
                The beam will be divided in equally spaced points and all results (displacement, momentum, shear) will be calculated to these points.
                Default value is 1.4.
            
            maximum_displacement_allowed : number, optional
                For each beam element, compare its maximum displacement with maximum_displacement_allowed(beam_element_length).
                This is used to solve the ELS shown in NBR 6118.
                If a beam_element length is 120cm, its maximum displacement is 1cm and maximum_displacement_allowed is 120/250=0.45cm < 1cm. Therefore, in this condition, the ELS step will raise an error.
                Default value is lambda beam_element_length : beam_element_length/250.
                
            available_long_steel_bars : AvailableLongConcreteSteelBar, optional
                Define the available longitudinal steel bars. 
                You can set the available diameters, cost_by_meter, fyw, E, etc.
                See more information in fc.AvailableLongConcreteSteelBar docstring.
                Default AvailableLongConcreteSteelBar([8]) which means:
                
                - 8mm diameter;
                - 0.5cmˆ2 area;
                - R$2.0575 by meter cost;
                - fyw equal to 50kN/cmˆ2;
                - Young Modulus (E) is 21000kN/cmˆ2;
                - Max number of steel in the section is 200;
                - Surface type is ribbed.
                
            bar_steel_removal_step : int, optional
                Define the step during the removal of the bar. Instead of taking the steel bars one by one, the bar_steel_removal_step will make the removal less constant.
                I makes the building process easier. 
                Default value is 2.
                
            bar_steel_max_removal : int, optional
                Define the max times it is possible to remove the bar.
                Default value is 100.
                
            available_transv_steel_bars : AvailableLongConcreteSteelBar
                Define the available longitudinal steel bars. 
                You can set the available diameters, cost_by_meter, fyw, E, etc.
                See more information in fc.AvailableLongConcreteSteelBar docstring or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
                Default AvailableLongConcreteSteelBar([8]) which means:
                
                - 8mm diameter;
                - 0.5cmˆ2 area;
                - R$2.0575 by meter cost;
                - The longitudinal space between transversal steel are multiple of 5;
                - fyw equal to 50kN/cmˆ2;
                - Transversal bar inclination angle of 90 degrees;
                - Tilt angle of compression struts of 45 degree.
            
            tilt_angle_of_compression_struts : number
                Tilt angle of compression struts in degrees.
                Default 45 degrees.
            
            available_concrete : AvailableConcrete
                Define the available concrete. 
                You can set the available fck, cost_by_m3, aggressiveness and aggregate.
                See more information in fc.AvailableConcrete docstring or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
                Default AvailableConcrete() which means:
                
                - 30 MPa;
                - R$353.30 by meterˆ3;
                - The aggressiveness is 3;
                - Aggregate is granite.
                - Biggest aggregate dimension is 1.5cm.
            
            time_begin_long_duration : number, optional
                The time, in months, relative to the date of application of the long-term load
                Default value is 0.
            
            lifetime_structure : number, optional
                The time, in months, when the value of the deferred arrow is desired;
                Default value is 70.
            
            verbose : bool, optional
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
        self.tilt_angle_of_compression_struts = tilt_angle_of_compression_struts
        self.available_long_steel_bars = available_long_steel_bars
        self.available_transv_steel_bars = available_transv_steel_bars
        self.available_concrete = available_concrete
        self.time_begin_long_duration = time_begin_long_duration
        self.lifetime_structure = lifetime_structure
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
        """
            Returns necessary steel area given the position and momentum.
            
            Parameters
            ----------
            **options
                
                ``division``:
                    Number of divisions equally spaced (`int`).
                ``x_begin``:
                    Begin of the x_axis (`number`).
                ``x_end``:
                    End of the x_axis (`number`).
                
            Returns
            -------
            x : list of number
                X axis in cm.
                
            displacement : list of number
                Vertical displacement value in cm.
                
        """ 
        x, y = self.getDisplacementDiagram(**options)
        return x, y*(self._time_function_coefficient(self.lifetime_structure)-self._time_function_coefficient(self.time_begin_long_duration))
    
    def plotConcreteDisplacementDiagram(self, **options):
        """
            Apply concrete_beam.getConcreteDisplacementDiagram for options["division"] parts of the beam.
            
            Parameters
            ----------
            **options
                
                ``division``:
                    Number of divisions equally spaced (`int`).
                ``x_begin``:
                    Begin of the x_axis (`number`).
                ``x_end``:
                    End of the x_axis (`number`).
                
            Returns
            -------
            x : list of number
                The x position of the division in cm
            
            y : list of number
                The value of displacement for each x.
        """
        options["division"] = options["division"] if options.get("division") else self.division
        x, y = self.getConcreteDisplacementDiagram(**options)
        plt.plot(x, y)
            
    @staticmethod
    def _time_function_coefficient(t):
        if t>70: return 2
        return 0.68*(0.996**t)*t**0.32 
    
    def solve_ELS(self):
        """
            Starts the process of solution for ELS (Estado Limite de Serviço)
        """
        self.initial_beam_elements = self._toConcreteBeamElements(self.initial_beam_elements)
        self.solve_displacement()
        for beam_element in self.initial_beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            _, y = self.getConcreteDisplacementDiagram(x_begin=x_begin, x_end=x_end, division=200)
            max_disp = self.maximum_displacement_allowed(beam_element.length)
            if max(abs(y)) > max_disp:
                raise Exception("Displacement too big between x={}cm and x={}cm. Maximum allowed is {}cm, but the beam lement reached {}cm".format(
                    x_begin, x_end, max_disp, max(abs(y))))
    
    def getShearDesignDiagram(self, **options):
        """
            Apply beam.getShearDiagram for options["division"] parts of the beam and multiplies by concrete_beam.design_factor.
            
            Parameters
            ----------
            **options
                
                ``division``:
                    Number of divisions equally spaced (`int`). Default concrete_beam.division.
                ``x_begin``:
                    Begin of the x_axis (`number`).
                ``x_end``:
                    End of the x_axis (`number`).
                
                
            Returns
            -------
            x : list of number
                The x position of the division in cm
            
            y : list of number
                The value of shear for each x.
        """
        options["division"] = options["division"] if options.get("division") else self.division
        x, shear_diagram = self.getShearDiagram(**options)
        return x, self.design_factor*shear_diagram
    
    def plotShearDesignDiagram(self, **options):
        """
            Simply applies the beam.getShearDesignDiagram method results (x,y) to a plot with plt.plot(x, y).

            Parameters
            ----------
            **options
                
                ``division``:
                    Number of divisions equally spaced (`int`).
                ``x_begin``:
                    Begin of the x_axis (`number`).
                ``x_end``:
                    End of the x_axis (`number`).
                
        """
        x, y = self.getShearDesignDiagram(**options)
        plt.plot(x, y)
    
    def plotTransversalInX(self, x):
        """
            Plot an image of the transversal section with the longitudinal and transversal steel.

                Call signatures:

                    concrete_beam.plotTransversalInX.getSteelArea(x)
                    
            Returns
            -------
            fig
                Figure generated by matplotlib.
                
            ax
                Axis generated by matplotlib.
                
        """
        positive_bars, negative_bars = self.long_steel_bars.getPositiveandNegativeLongSteelBarsInX(x=x)
        transversal_bar = self.transv_steel_bars.getTransversalBarAfterX(x)
        
        _, beam_element = self.getBeamElementInX(x)
        material, section = beam_element.material, beam_element.section
        
        fig, ax = section.plot()
        fig, ax = transversal_bar.plot(fig=fig, ax=ax, c=material.c)
        fig, ax = positive_bars.plotTransversal(self, x, fig=fig, ax=ax)
        fig, ax = negative_bars.plotTransversal(self, x, fig=fig, ax=ax)

    def solve_transv_steel(self):
        """
            Starts the process of solution for the used transversal steel.
        """
        self.transv_steel_bars_solution_info = fc.TransvSteelBarSolve(concrete_beam=self,
                                                                        fyk=self.available_transv_steel_bars.fyw,
                                                                        theta_in_degree= self.tilt_angle_of_compression_struts,
                                                                        alpha_in_degree = self.available_transv_steel_bars.inclination_angle)
        self.transv_steel_bars = self.transv_steel_bars_solution_info.steel_bars
    
    def solve_long_steel(self):
        """
            Starts the process of solution for the used longitudinal steel.
        """
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