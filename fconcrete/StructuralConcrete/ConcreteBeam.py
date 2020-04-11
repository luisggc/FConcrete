from fconcrete.Structural.Beam import Beam
from fconcrete.StructuralConcrete import AvailableLongConcreteSteelBar, AvailableTransvConcreteSteelBar, AvailableConcrete
from fconcrete.Structural.BeamElement import BeamElement, BeamElements
from fconcrete.helpers import timeit, make_dxf, to_pandas
import fconcrete as fc
import numpy as np
import matplotlib.pyplot as plt
import time
from fconcrete.StructuralConcrete.AvailableMaterials import solve_cost
import datetime

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
                
        available_transv_steel_bars : AvailableTransvConcreteSteelBar
            Same constant from input.
            Define the available transversal steel bars. 
            You can set the available diameters, cost_by_meter, fyw, E, etc.
            See more information in fc.AvailableTransvConcreteSteelBar docstring or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
            Default AvailableTransvConcreteSteelBar([8]) which means:
            
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
                 division=200,
                 maximum_displacement_allowed=lambda beam_element_length : beam_element_length/250,
                 available_long_steel_bars=AvailableLongConcreteSteelBar(),
                 bar_steel_removal_step=2,
                 bar_steel_max_removal=100,
                 available_transv_steel_bars=AvailableTransvConcreteSteelBar(),
                 tilt_angle_of_compression_struts=45,
                 available_concrete=AvailableConcrete(),
                 time_begin_long_duration=0,
                 lifetime_structure=70,
                 verbose = False,
                 max_relative_diff_of_steel_height = 0.02,
                 consider_own_weight = True,
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
                See more information in fc.AvailableLongConcreteSteelBar docstring  or the :doc:`AvailableMaterials Class <../fconcrete.StructuralConcrete.AvailableMaterials>` documentation.
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
                - The longitudinal spaces between transversal steel are multiple of 5;
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
            
            max_relative_diff_of_steel_height: number, optional
                Maximum value for relative difference of the beam section "d" value.
                The relative difference is calculated taking the module of the sum of all previous d's less the sum for the calculated value of d divided by the sum of all previous calculated d's
                If this values is greater than the max_relative_diff_of_d, all concrete_beam is recalculated.
                The initial value of d is set to be 0.8*height.
                Default value is 0.02.
            
            consider_own_weight : bool, optional
                Consider the load generated by the weight of the concrete.
                Default value is True.
        """
        start = time.time()
        
        beam_elements, loads = self._input_to_concrete_properties(
            nodes=nodes,
            beam_elements=beam_elements,
            material=available_concrete.material,
            section=section,
            consider_own_weight = consider_own_weight,
            loads=loads
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
        self.max_relative_diff_of_steel_height = max_relative_diff_of_steel_height
            
        if options.get("solve_transv_steel") != False:
            timeit(verbose, "Solve transv steel")(self.solve_transv_steel)()
            
        if options.get("solve_long_steel") != False:
            self.solve_long_steel()
        
        if options.get("solve_ELS") != False:
            timeit(verbose, "Solve ELS")(self.solve_ELS)()
        
        if options.get("solve_cost") != False:
            self.solve_cost()
            # d value is the initially with 0.8*height. This function check if initial guess is ok.
            self.checkRecalculationOfD()
        
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
        _, ax = plt.subplots()
        ax.plot(x, y)
        return make_dxf(ax, **options)
            
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
        _, ax = plt.subplots()
        ax.plot(x, y)
        return make_dxf(ax, **options)
    
    def plotTransversalInX(self, x, **options):
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
        
        ax, _ = section.plot()
        ax, _ = transversal_bar.plot(ax=ax, c=material.c)
        ax, _ = positive_bars.plotTransversal(self, x, ax=ax)
        ax, _ = negative_bars.plotTransversal(self, x, ax=ax)
        return make_dxf(ax, **options)

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
    def _input_to_concrete_properties(**inputs):
        nodes, beam_elements, section, material = inputs.get("nodes"), inputs.get("beam_elements"), inputs.get("section"), inputs.get("material")
        if nodes and section:
            section = fc.ConcreteSection.setSteelHeight(section)
            if len(nodes) == 1: raise Exception("Must contain at least 2 nodes to create a beam")
            beam_elements = []
            for i in range(0,len(nodes)-1):
                beam_elements = [*beam_elements, fc.BeamElement([nodes[i], nodes[i+1]], section, material)]
        elif beam_elements and section:
            beam_elements = BeamElements.create(beam_elements)
            beam_elements = beam_elements.changeProperty("material", lambda x:material)
            section = fc.ConcreteSection.setSteelHeight(section)
            beam_elements = beam_elements.changeProperty("section", lambda x:section)
        elif beam_elements:
            beam_elements_modified = []
            for beam_element in beam_elements:
                section = fc.ConcreteSection.setSteelHeight(beam_element.section)
                beam_element.section = section
                beam_elements_modified = [*beam_elements_modified, beam_element]
            beam_elements = beam_elements_modified
            
        loads = inputs["loads"]
        if(inputs.get("consider_own_weight")==True):
            for beam_element in beam_elements:
                q = -beam_element.section.area*25/1000000
                loads = [*loads, fc.Load.UniformDistributedLoad(q, x_begin=beam_element.n1.x, x_end=beam_element.n2.x)]
    
        return beam_elements, loads
    
    def _toConcreteBeamElements(self, beam_elements):
        for beam_element in beam_elements:
            x_begin = beam_element.n1.x
            x_end = beam_element.n2.x
            section = beam_element.section
            material = beam_element.material
            
            I = section.I
            y_cg = section.y_cg
            bw = section.bw
            d = section.positive_steel_height
            
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
    
    def solve_cost(self):
        """
            Starts the process of solution for the cost table.
        """
        self.cost, self.cost_table, self.subtotal_table = solve_cost(self)
        self.pd_cost_table, self.pd_subtotal_table = to_pandas(self.cost_table), to_pandas(self.subtotal_table)
        
    def checkRecalculationOfD(self):
        """
            Recalculate all beam with the true value of steel height (d)
        """
        while True:
            x_changes = np.concatenate((self.long_steel_bars.long_begins, self.long_steel_bars.long_ends))
            x_changes = x_changes[np.isin(x_changes, self.beam_elements.nodes.x, invert=True)]
            x_changes = np.unique(x_changes[(x_changes>=0) & (x_changes<=self.length)])

            nodes_change = [ fc.Node.Crimp(x) for x in x_changes ]
            new_nodes = fc.Nodes(np.concatenate((nodes_change, self.beam_elements.nodes)))
            new_nodes = new_nodes[np.argsort(new_nodes.x)]

            previous_ds_positive, previous_ds_negative, diff_positive, diff_negative = 0, 0, 0, 0
            beam_elements = []

            for i in range(0, len(new_nodes)-1):
                current_x = new_nodes[i].x
                next_x = new_nodes[i+1].x
                middle_x = (current_x+next_x)/2

                positive_bars, negative_bars = self.long_steel_bars.getPositiveandNegativeLongSteelBarsInX(x=middle_x)
                positive_transversal_position, negative_transversal_position = positive_bars.getBarTransversalPosition(self, x=middle_x), negative_bars.getBarTransversalPosition(self, x=middle_x)

                transversal_position = negative_transversal_position if len(positive_transversal_position)==0 else (
                    positive_transversal_position if len(negative_transversal_position)==0 else np.concatenate((
                        positive_transversal_position,
                        negative_transversal_position
                    ))
                )

                _, beam_element = self.getBeamElementInX(middle_x)
                section, material = beam_element.section, beam_element.material
                height = section.height

                _, y, _, area = transversal_position.T

                y_c_negative = (y[y >= (height/2)] @ area[y >= (height/2)])/sum(area[y >= (height/2)]) if sum(y >= (height/2)) else 0
                y_c_positive = height - (y[y < (height/2)] @ area[y < (height/2)])/sum(area[y < (height/2)]) if sum(y < (height/2)) else 0

                new_positive_steel_height, previous_positive_steel_height = (y_c_positive), section.positive_steel_height
                new_negative_steel_height, previous_negative_steel_height = (y_c_negative), section.negative_steel_height

                previous_ds_positive += 0 if new_positive_steel_height else previous_positive_steel_height
                previous_ds_negative += 0 if new_negative_steel_height else previous_negative_steel_height
                diff_positive += abs(previous_positive_steel_height-new_positive_steel_height if new_positive_steel_height else 0)
                diff_negative += abs(previous_negative_steel_height-new_negative_steel_height if new_negative_steel_height else 0)

                new_section = fc.Rectangle(section.width(), section.height)
                new_section = fc.ConcreteSection.setSteelHeight(new_section, new_positive_steel_height, new_negative_steel_height)

                new_beam_element = fc.BeamElement([new_nodes[i], new_nodes[i+1]], new_section, material)
                beam_elements = [*beam_elements, new_beam_element]
            
            relative_positive_diff = diff_positive/previous_ds_positive if previous_ds_positive else 0
            relative_negative_diff = diff_negative/previous_ds_negative if previous_ds_negative else 0
            
            if max(relative_positive_diff, relative_negative_diff) > self.max_relative_diff_of_steel_height:
                self.beam_elements = fc.BeamElements(beam_elements)
                self.solve_long_steel()
                self.solve_transv_steel()
                self.solve_ELS()
                self.solve_cost()
            else:
                break
    
    def saveas(self,
               file_name=False,
               column_height = 30,
               gap = 50,
               scale_y_long_bar = 10,
               transversal_plot_positions=[]
               ):
        """
            Save all essential plots to a dxf file.
        """
        file_name = datetime.datetime.now().strftime("%d-%m-%Y %H-%m-%S") if file_name == False else file_name
        max_height = max([ section.height for section in self.beam_elements.sections ])

        # Positive Long bar draw
        positive_long_steel_bar = fc.LongSteelBars(self.long_steel_bars[self.long_steel_bars.areas > 0])
        start_y_bottom = -abs(positive_long_steel_bar.areas).max(initial=0)*scale_y_long_bar - 2*gap - max_height
        _, msp = self.long_steel_bars.plot(scale_y=scale_y_long_bar, xy_position=(0,start_y_bottom))

        # Plot transversal bars
        start_y = gap + max_height
        _, msp = self.transv_steel_bars.plotLong(msp=msp, xy_position=(0,-start_y))

        # Beam draw
        max_height = max([ section.height for section in self.beam_elements.sections ])
        start_y = column_height
        _, msp = self.plot(msp=msp, column_height=column_height, xy_position=(0,start_y))

        # Negative Long Bar draw
        negative_long_steel_bar = fc.LongSteelBars(self.long_steel_bars[self.long_steel_bars.areas < 0])
        start_y += max_height + abs(negative_long_steel_bar.areas).max(initial=0)*scale_y_long_bar + gap
        _, msp = negative_long_steel_bar.plot(msp=msp, scale_y=scale_y_long_bar, xy_position=(0,start_y))

        # Momentum decalaged draw
        _, mm, mn = self.long_steel_bars_solution_info.getDecalagedMomentumDesignDiagram()
        mm, mn = mm[np.invert(np.isnan(mm))], mn[np.invert(np.isnan(mn))]
        minimum_momentum, maximum_momentum = abs(min(mn.min(initial=0), mm.min(initial=0), 0)), abs(max(mn.max(initial=0), mm.max(initial=0), 0))
        start_y += minimum_momentum + gap

        _, msp = self.long_steel_bars_solution_info.plotDecalagedMomentumDesignDiagram(msp=msp, xy_position=(0,start_y))

        # Shear draw

        #x, sd = self.getShearDesignDiagram()
        #minimum_shear, maximum_shear = abs(min(min(sd), min(sd), 0)), abs(max(max(sd), max(sd), 0))
        start_y += maximum_momentum + gap
        ax, msp = self.plotShearDesignDiagram(msp=msp, xy_position=(0,start_y))

        transversal_x = self.length
        for position in transversal_plot_positions:
            transversal_x += gap + self.getBeamElementInX(position)[1].section.width(0)
            ax, msp = self.plotTransversalInX(position, msp=msp, xy_position=(transversal_x, 0))

        viewport_height = start_y+abs(start_y_bottom)
        msp.doc.set_modelspace_vport(height=viewport_height, center=(transversal_x/2, start_y_bottom+viewport_height/2))

        msp.doc.saveas("FConcrete Draw {}.dxf".format(file_name))

        return ax, msp
    
    def __name__(self):
        return "ConcreteBeam"