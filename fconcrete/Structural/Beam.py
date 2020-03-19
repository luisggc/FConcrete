from fconcrete.Structural.BeamElement import BeamElement, BeamElements
from fconcrete.Structural.Load import Load, Loads
from fconcrete.Structural.Node import Nodes
from fconcrete.helpers import cond, make_dxf, getAxis
from fconcrete.config import e
import copy
import numpy as np
import warnings
import matplotlib.pyplot as plt


class Beam:
    """
        Structural Beam.\n
        Note for this documentation: "Not only the ones provided by the initial beam_Elements" means that internally the Beam automatically creates some nodes even if it was not created for the user initially. It happens in Load.x_begin and Load.x_end. 
        
        Attributes
        ----------
        U: list of number
            Displacement in the nodes.

        beam_elements: BeamElements
            BeamElements instance of beam_elements, not only the ones provided by the initial beam_Elements.

        beams_quantity: number
            Number of beam_elements, not only the ones provided by the initial beam_Elements.

        external_loads: Loads
            loads argument but used as a Loads class. Same as fconcrete.Structural.Load.Loads.create(loads).

        initial_beam_elements: array of BeamElement
            beam_elements argument used when the instance is created.

        length: number
            Length of the beam. Can also use len(beam).
        
        loads: Loads
            Loads instance with all efforts in the beam. Including the load given by the supports.
            
        nodal_efforts: list of number
            The nodal efforts that happens in all nodes, not only the ones provided by the initial beam_Elements.

        nodes: Nodes
            Nodes instance of the beam, not only the ones provided by the initial beam_Elements.
            
        x_begin: number
            Where the beam starts, in cm.

        x_end: number
            Where the beam ends, in cm.
    """
    def __init__(self, loads, beam_elements, **options):
        """
            Returns a concrete_beam element.
            
                Call signatures:

                    fc.Beam(loads, beam_elements, **options)

                >>> n1 = fc.Node.SimpleSupport(x=0)
                >>> n2 = fc.Node.SimpleSupport(x=400)
                >>> n3 = fc.Node.SimpleSupport(x=800)
                >>> beam_element_1 = fc.BeamElement([n1, n2])
                >>> beam_element_2 = fc.BeamElement([n2, n3])
                >>> load_1 = fc.Load.UniformDistributedLoad(-0.000001, x_begin=0, x_end=1)
                 
                >>> beam = fc.Beam(
                >>>     loads = [f1],
                >>>     beam_elements = [beam_element_1, beam_element_2],
                >>> )
            
            Parameters
            ----------
            loads : [Load]
                Define the loads supported for the beam.
            
            beam_elements : [BeamElement], optional
                Define the beam_elements that, together, makes the whole Beam. 
        """
        beam_elements = BeamElements.create(beam_elements)
        external_loads = Loads.create(loads)
        self.initial_beam_elements = beam_elements
        beam_elements = self._createIntermediateBeams(external_loads, beam_elements)
        self.x_begin, self.x_end = beam_elements.nodes[0].x, beam_elements.nodes[-1].x
        
        self.external_loads = external_loads
        self.beam_elements = beam_elements
        
        self.length = sum(beam_elements.length)
        self.beams_quantity = len(beam_elements)
        
        if options.get("solve_structural") != False:
            self.solve_structural()
            if options.get("solve_displacement") != False:
                self.solve_displacement()
        
    def solve_structural(self):
        """
            Starts the process of solution for the structural beam.
        """
        nodal_efforts = self._getSupportReactions()
        self.nodal_efforts = nodal_efforts
        nodes = Nodes(self.beam_elements.nodes)
        self.nodes = nodes
        loads = self.external_loads
        for index, node in enumerate(nodes.nodes):
            loads = loads.add(
                [Load(nodal_efforts[index*2], nodal_efforts[index*2+1], node.x, node.x)]
                )
        self.loads = loads
                   
    @staticmethod
    def _createIntermediateBeams(loads, bars):
        for load in loads.loads:
            bars = bars.split(load.x_begin)
            bars = bars.split(load.x_end)
        
        return bars

    def matrix_rigidity_global(self):
        """
            Returns the global rigidity matrix. Also known by the letter "K". 
        """
        matrix_rigidity_row = 2*self.beams_quantity+2
        matrix_rigidity_global = np.zeros(
            (matrix_rigidity_row, matrix_rigidity_row))
        for beam_n, beam in enumerate(self.beam_elements):
            matrix_rigidity_global[beam_n*2:beam_n*2+4,
                                   beam_n*2:beam_n*2+4] += beam.get_matrix_rigidity_unitary()
        return matrix_rigidity_global

    def _get_beams_efforts(self):
        beams_efforts = np.zeros(self.beams_quantity*4)

        for load in self.external_loads.loads:
            if (load.x == self.x_end):
                load.x = self.x_end - e
            force_beam, beam_element = self.getBeamElementInX(load.x)

            beams_efforts[4*force_beam:4*force_beam+4] += BeamElement.get_efforts_from_bar_element(
                beam_element,
                load
            )

        # juntar vigas separadas em um vetor por nó
        bn = self.beams_quantity
        b = 2*np.arange(0, 2*bn+2, 1)
        b[1::2] = b[0::2]+1
        b[1] = b[-1] = b[-2] = 0
        mult_b = b != 0

        a = 2*(np.arange(0, 2*bn+2, 1)-1)
        a[0] = 0
        a[1::2] = a[0::2]+1

        return beams_efforts[a] + beams_efforts[b]*mult_b

    def _getSupportReactions(self):
        condition_boundary = self.beam_elements.condition_boundary
        beams_efforts = self._get_beams_efforts()
        matrix_rigidity_global = self.matrix_rigidity_global()

        matrix_rigidity_global_determinable = matrix_rigidity_global[condition_boundary, :][:, condition_boundary]
        beams_efforts_determinable = beams_efforts[condition_boundary]

        U = np.zeros(len(condition_boundary))
        U[condition_boundary] = np.linalg.solve(matrix_rigidity_global_determinable, beams_efforts_determinable)
        self.U = U
        F = matrix_rigidity_global @ U

        return beams_efforts - F
    

    def getBeamElementInX(self, x):
        """
            Get the beam element in x (in cm).

                Call signatures:

                    beam.getBeamElementInX(x)
            
            Parameters
            ----------
            x : number
                Position in the beam, in cm.
            
            Returns
            -------
            index : int
                The order of the beam_element in the structure.
                
            beam_element
                beam_element located in x.
                
        """
        index = 0 if x<=self.x_begin else -1 if x>=self.x_end else np.where(
        np.array([node.x for node in self.beam_elements.nodes]) <= x)[0][-1]
        bar_element = self.beam_elements[index]
        return index, bar_element
        
    def getInternalShearStrength(self, x):
        """
            Get the internal shear strength in a position x (in cm) or multiple positions.

                Call signatures:

                    beam.getInternalShearStrength(x)
            
            Parameters
            ----------
            x : number or list of number
                Position in the beam, in cm.
            
            Returns
            -------
            shear : number or list of number
                The internal value of the shear strength in kN.
                
        """
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end:
                return 0
            f_value = 0
            for load in self.loads.loads:
                f_value += load.force * \
                    cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
                f_value += load.q*cond(x-load.x_begin, order=load.order) - load.q*cond(
                    x-load.x_end, order=load.order) if load.x_begin != load.x_end else 0
            return f_value
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getInternalShearStrength(x_element) for x_element in x ])
        
    def getShearDiagram(self, **options):
        """
            Apply beam.getInternalShearStrength for options["division"] parts of the beam.
            
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
                The value of shear for each x.
        """
        return self._createDiagram(self.getInternalShearStrength, **options)

    def getInternalMomentumStrength(self, x):
        """
            Get the internal momentum strength in a position x (in cm) or multiple positions.

                Call signatures:

                    beam.getInternalMomentumStrength(x)
            
            Parameters
            ----------
            x : number or list of number
                Position in the beam, in cm.
            
            Returns
            -------
            x : list of number
                The x position of the division in cm
                
            momentum : number or list of number
                The internal value of the momentum strength in kNcm.
                
        """
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end:
                return 0
            f_value = 0
            for load in self.loads.loads:
                f_value += -load.momentum * \
                    cond(x-load.x_begin, singular=True) if load.x_begin == load.x_end else 0
                f_value += load.force * \
                    cond(x-load.x_begin, order=1) if load.order == 0 else 0
                f_value += (load.q*cond(x-load.x_begin, order=load.order+1) -
                            load.q*cond(x-load.x_end, order=load.order+1))/(load.order+1)
            return f_value
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getInternalMomentumStrength(x_element) for x_element in x ])
        
    def getMomentumDiagram(self, **options):
        """
            Apply beam.getInternalMomentumStrength for options["division"] parts of the beam.
            
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
                The value of momentum for each x.
        """
        return self._createDiagram(self.getInternalMomentumStrength, **options)
    
    def solve_displacement(self):
        """
            Starts the process of solution for the structural beam displacement.
        """
        nodes = self.initial_beam_elements.nodes
        null_displacement = nodes.x[nodes.condition_boundary[:, 0]==0]
        null_rotation = nodes.x[nodes.condition_boundary[:, 1]==0]
        
        x1 = null_displacement[0]
        rest1 = self.getDisplacement(x1)
        
        if len(null_displacement)>=2:
            x2 = null_displacement[-1]
            rest2 = self.getDisplacement(x2)
            c1 = -(rest1 - rest2)/(x1-x2)
            c2 = -rest1 - c1*x1
        elif len(null_rotation)>=1 and len(null_displacement)>=1:
            x2 = null_rotation[0]
            c1 = -self.getRotation(x2)

        c2 = -rest1 - c1*x1
        
        self._c1 = c1
        self._c2 = c2
    
    def getDisplacement(self, x):
        """
            Get the vertical displacement in a position x (in cm) or multiple positions.

                Call signatures:

                    beam.getDisplacement(x)
            
            Parameters
            ----------
            x : number or list of number
                Position in the beam, in cm.
            
            Returns
            -------
            displacement : number or list of number
                The vertical displacement of the beam in cm.
                
        """
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end: return 0
            f_value = 0
            _, single_beam_element_init = self.getBeamElementInX(x)
            
            for load in self.loads:
                _, single_beam_element = self.getBeamElementInX(x) #load.x_begin+e)
                l_value = -load.momentum * \
                    cond(x-load.x_begin, order=2)/2 if load.x_begin == load.x_end else 0
                l_value += load.force * \
                    cond(x-load.x_begin, order=3)/6 if load.order == 0 else 0
                l_value += (load.q*cond(x-load.x_begin, order=load.order+3) -
                            load.q*cond(x-load.x_end, order=load.order+3))/((load.order+1)*(load.order+2)*(load.order+3))
                f_value += l_value/single_beam_element.flexural_rigidity
            
            if not hasattr(self, "_c1"):
                return f_value*single_beam_element_init.flexural_rigidity
            
            return f_value + (self._c1*x+self._c2)/single_beam_element_init.flexural_rigidity
        
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getDisplacement(x_element) for x_element in x ])
        
        
    def getDisplacementDiagram(self, **options):
        """
            Apply beam.getDisplacement for options["division"] parts of the beam.
            
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
        return self._createDiagram(self.getDisplacement, **options)
    
    def getRotation(self, x):
        """
            Get the rotation in a position x (in cm) or multiple positions.

                Call signatures:

                    beam.getRotation(x)
            
            Parameters
            ----------
            x : number or list of number
                Position in the beam, in cm.
            
            Returns
            -------
            rotation : number or list of number
                The rotation value of the momentum strength in rad.
                
        """
        if isinstance(x, int) or isinstance(x, float):
            if x < self.x_begin or x > self.x_end: return 0
            f_value = 0
            _, single_beam_element_init = self.getBeamElementInX(x)
            for load in self.loads:
                _, single_beam_element = self.getBeamElementInX(load.x_begin+e)
                l_value = -load.momentum * \
                    cond(x-load.x_begin, order=1) if load.x_begin == load.x_end else 0
                l_value += load.force * \
                    cond(x-load.x_begin, order=2)/2 if load.order == 0 else 0
                l_value += (load.q*cond(x-load.x_begin, order=load.order+2) -
                            load.q*cond(x-load.x_end, order=load.order+2))/((load.order+1)*(load.order+2))
                f_value += l_value/single_beam_element.flexural_rigidity
                
            if not hasattr(self, "_c1"):
                return f_value*single_beam_element.flexural_rigidity
            return f_value + self._c1/single_beam_element_init.flexural_rigidity
        
        elif isinstance(x, np.ndarray) or isinstance(x, list):
            return np.array([ self.getRotation(x_element) for x_element in x ])
    
    def getRotationDiagram(self, **options):
        """
            Apply beam.getRotation for options["division"] parts of the beam.
            
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
                The value of rotation for each x.
        """
        return self._createDiagram(self.getRotation, **options)
    
    def _createDiagram(self, function, division=1000, x_begin="begin", x_end="end", **options):
        x_begin = self.x_begin+e if x_begin=="begin" else x_begin
        x_end = self.x_end-e if x_end=="end" else x_end
        x = np.linspace(x_begin, x_end, division)
        y = np.array([function(x_i) for x_i in x])
        return x, y
    
    def plotMomentumDiagram(self, **options):
        """
            Simply applies the beam.getMomentumDiagram method results (x,y) to a plot with plt.plot(x, y).\n
            Also invert y axis.
            
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
        _, ax = plt.subplots()
        x, y = self.getMomentumDiagram(**options)
        plt.gca().invert_yaxis()
        ax.plot(x, y)
        return make_dxf(ax, **options)
        
    def plotShearDiagram(self, **options):
        """
            Simply applies the beam.getShearDiagram method results (x,y) to a plot with plt.plot(x, y).

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
        x, y = self.getShearDiagram(**options)
        _, ax = plt.subplots()
        ax.plot(x, y)
        return make_dxf(ax, **options)
        
    def plotDisplacementDiagram(self, **options):
        """
            Simply applies the beam.getDisplacementDiagram method results (x,y) to a plot with plt.plot(x, y).
        
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
        x, y = self.getDisplacementDiagram(**options)
        _, ax = plt.subplots()
        ax.plot(x, y)
        return make_dxf(ax, **options)
        
    def plotRotationDiagram(self, **options):
        """
            Simply applies the beam.getRotationDiagram method results (x,y) to a plot with plt.plot(x, y).
        
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
        x, y = self.getRotationDiagram(**options)
        _, ax = plt.subplots()
        ax.plot(x, y)
        return make_dxf(ax, **options)
    
    def plot(self, column_height=30, beam_color="b", **options):
        _, ax = getAxis()

        first_beam_element = self.beam_elements[0]
        last_beam_element = self.beam_elements[-1]
        ax.plot([first_beam_element.n1.x, first_beam_element.n1.x], [first_beam_element.section.y0, first_beam_element.section.y0+first_beam_element.section.height], color=beam_color)
        ax.plot([last_beam_element.n2.x, last_beam_element.n2.x], [last_beam_element.section.y0, last_beam_element.section.y0+last_beam_element.section.height], color=beam_color)

        # print beam
        for beam_number, beam_element in enumerate(self.beam_elements):
            positions = [beam_element.n1.x, beam_element.n2.x]
            ax.plot(positions, np.repeat(beam_element.section.y0,2), color=beam_color)
            ax.plot(positions, np.repeat(beam_element.section.y0+beam_element.section.height,2), color=beam_color)
            if beam_number+1 != len(self.beam_elements):
                ax.plot([beam_element.n2.x, beam_element.n2.x], [beam_element.section.y0+beam_element.section.height, self.beam_elements[beam_number+1].section.y0+self.beam_elements[beam_number+1].section.height], color=beam_color)

        # print column
        for node in self.initial_beam_elements.nodes:
            if node.length != 0:
                ax.plot((node.x-node.length/2, node.x-node.length/2), (0, -column_height), color=beam_color)
                ax.plot((node.x+node.length/2, node.x+node.length/2), (0, -column_height), color=beam_color)
                
        return make_dxf(ax, **options)

    def __name__(self):
        return "Beam"
    
    def __repr__(self):
        return str(self.__dict__)

    def copy(self):
        """
            Makes a deep copy of the instance of Beam.
        """
        return copy.deepcopy(self)
    
    