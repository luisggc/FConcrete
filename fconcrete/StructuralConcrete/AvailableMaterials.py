import numpy as np
from math import sin, tan,  pi
from fconcrete.StructuralConcrete.Concrete import Concrete

#https://loja.arcelormittal.com.br/vergalhao-ca50-soldavel-63mm/p
class AvailableLongConcreteSteelBar:
    """
        Define the available longitudinal steel bars. 
        You can set the available diameters, cost_by_meter, fyw, E, etc.
        See more information in fc.AvailableLongConcreteSteelBar() docstring.
        For example, AvailableLongConcreteSteelBar([8]) means:
        
        - 8mm diameter;
        - 0.5cmˆ2 area;
        - R$2.0575 by meter cost;
        - fyw equal to 50kN/cmˆ2;
        - Young Modulus (E) is 21000kN/cmˆ2;
        - Max number of steel in the section is 200;
        - Surface type is ribbed.
    """
    def __init__(self,
                 diameters=[8],
                 diameters_to_area={
                        6.3: 0.315,
                        8: 0.5,
                        10: 0.8,
                        12.5: 1.25,
                        16: 2,
                        20: 3.15,
                        25: 5,
                        32: 8,
                    },
                 cost_by_meter={
                        6.3: 15.39/12,
                        8: 24.69/12,
                        10: 36.89/12,
                        12.5: 54.79/12,
                        16: 89.79/12,
                        20: 140.29/12,
                        25: 219.09/12,
                        32: 402.39/12,
                    },
                 fyw = 50,
                 E = 21000,
                 max_number=200,
                 surface_type="ribbed"):
        """
            Returns a AvailableLongConcreteSteelBar instance.
            
            Parameters
            ----------
            diameter : list of number, optional
                Possible list of diameter in cm.
            
            diameters_to_area : dict, optional
                For each diameter (key), set the value of the area.
                
            cost_by_meter : dict, optional
                For each diameter (key), set the of cost by meter.
                
            fyw : number, optional
                Define the characteristic resistance of the steel in kN/cmˆ2.
                
            E : number, optional
                Define the Young Modulus (E) in kN/cmˆ2
                Default is 21000kN/cmˆ2.
            
            max_number : int, optional
                Max number of steel in the section.
                Default is 200.
            
            surface_type : {'ribbed', 'plain', 'carved'}, optional
                Surface type of the steel.
                Default is ribbed.
        """ 
        try:
            areas = [diameters_to_area[diameter] for diameter in diameters]
        except:
            raise Exception("Must provide a valid diameter to area dict")
        fyd = fyw/1.15
        diameters = np.array(diameters)
        areas = np.array(areas)
        diameters_loop = np.tile(diameters/10, max_number-1)
        # Single steel bar use not allowed, that is why range starts at 2
        areas_loop = np.concatenate([ areas*(i) for i in range(2, max_number+1)])
        number_of_bars = areas_loop/np.tile(areas,max_number-1)
        table_of_positive_steel = np.stack((number_of_bars, diameters_loop, areas_loop), axis=1)
        
        table_of_negative_steel = np.stack((number_of_bars, -diameters_loop, -1*areas_loop), axis=1)
        table_of_positive_and_negative_steel = np.vstack([table_of_negative_steel, table_of_positive_steel])
        
        table = np.array(table_of_positive_and_negative_steel[
            table_of_positive_and_negative_steel[:,2].argsort()
        ])
        self.table = table
        self.fyw = fyw
        self.fyd = fyd
        self.E = E
        self.diameters = diameters
        self.diameters_to_area = diameters_to_area
        self.surface_type = surface_type
        self.cost_by_meter = cost_by_meter
        
        
class AvailableTransvConcreteSteelBar:
    """
        Define the available transversal steel bars. 
        You can set the available diameters, cost_by_meter, fyw, E, etc.
        See more information in fc.AvailableTransvConcreteSteelBar docstring.
        Default AvailableTransvConcreteSteelBar([8]) which means:
        
        - 8mm diameter;
        - 0.5cmˆ2 area;
        - R$2.0575 by meter cost;
        - The longitudinal space between transversal steel are multiple of 5;
        - fyw equal to 50kN/cmˆ2;
        - Transversal bar inclination angle of 90 degrees;
        - Tilt angle of compression struts of 45 degrees.
    """
    def __init__(self,
                 diameters=[8],
                 diameters_to_area={
                        6.3: 0.315,
                        8: 0.5,
                        10: 0.8,
                        12.5: 1.25,
                        16: 2,
                        20: 3.15,
                        25: 5,
                        32: 8,
                    },
                 cost_by_meter={
                        6.3: 15.39/12,
                        8: 24.69/12,
                        10: 36.89/12,
                        12.5: 54.79/12,
                        16: 89.79/12,
                        20: 140.29/12,
                        25: 219.09/12,
                        32: 402.39/12,
                    },
                 space_is_multiple_of=[5],
                 fyw = 50,
                 inclination_angle = 90,
                 ):
        """
            Returns a AvailableLongConcreteSteelBar instance.
            
            Parameters
            ----------
            diameter : list of number, optional
                Possible list of diameter in cm.
            
            diameters_to_area : dict, optional
                For each diameter (key), set the value of the area.
                
            cost_by_meter : dict, optional
                For each diameter (key), set the of cost by meter.
                
            space_is_multiple_of : list of number, optional
                The longitudinal spaces between transversal steel is multiple of the number of space_is_multiple_of list.
                Default is [5].
            
            fyw : number, optional
                Define the characteristic resistance of the steel in kN/cmˆ2.
                
            inclination_angle : number, optional
                Transversal bar inclination angle in degrees.
                Default is 90 degrees.
        """ 
            
        try:
            areas = [diameters_to_area[diameter] for diameter in diameters]
        except:
            raise Exception("Must provide a valid diameter to area dict")
        
        possible_spaces = np.array([])
        for multiple in space_is_multiple_of:
            possible_spaces = np.concatenate((possible_spaces,multiple*np.arange(1,30)))
        possible_spaces = np.unique(possible_spaces[possible_spaces <= 30])
        
        areas = [ diameters_to_area[diameter] for diameter in diameters ]
        diameters_loop = np.tile(diameters, len(possible_spaces))/10
        spaces_loop = np.repeat(possible_spaces, len(diameters))
        areas_loop = 2*np.tile(areas, len(possible_spaces))

        table = np.transpose([
            diameters_loop,
            spaces_loop,
            areas_loop,
            areas_loop/spaces_loop
        ])

        fyd = fyw/1.15
        diameters = np.array(diameters)
        
        self.fyw = fyw
        self.fyd = fyd
        self.table = table[table[:,3].argsort()]
        
        self.diameters = diameters
        self.diameters_to_area = diameters_to_area
        self.cost_by_meter = cost_by_meter
        self.inclination_angle = inclination_angle
        
#https://servicos.compesa.com.br/wp-content/uploads/2016/02/TABELA_COMPESA_2016_SEM_DESONERACAO_E_SEM_ENCARGOS_COMPLEMENTARES.pdf
class AvailableConcrete():
    """
        Define the available concrete. 
        You can set the available fck, cost_by_m3, aggressiveness and aggregate.
        See more information in fc.AvailableConcrete docstring.
        For example, AvailableConcrete() means:
        
        - 30 MPa;
        - R$353.30 by meterˆ3;
        - The aggressiveness is 3;
        - Aggregate is granite;
        - Biggest aggregate dimension is 1.5cm.
    """
    def __init__(self,
                 fck=30,
                 cost_by_m3=None,
                 aggressiveness=3,
                 aggregate='granite',
                 biggest_aggregate_dimension=1.5
                 ):
        """
            Returns a AvailableLongConcreteSteelBar instance.
            
            Parameters
            ----------
            fck : number
                Define the characteristic resistance of the concrete.
                If it is a number, default unit is MPa, but also [force]/[length]**2 unit can be given. Example:
                '20kN/cm**2', '10Pa', etc
            
            cost_by_m3 : number, optional
                Cost by mˆ3 of the concrete.
                If fck is 25, 30, 35 or 40, this value by default is set to 331.65, 353.30, 373.21, 385.36, respectively.
                
            aggressiveness : int
                Aggressiveness value from 1 (very low) to 4 (very height)

            aggregate : {'basalt', 'diabase', 'granite', 'gneiss', 'limestone', 'sandstone'}
                Aggregate type.
                
            biggest_aggregate_dimension : number, optional
                Maximum dimension characteristic of the biggest aggregate, in cm.
                Default value is 1.5.
        """ 
        if cost_by_m3 == None:
            try:
                cost_by_m3_dict = {
                    25: 331.65,
                    30: 353.30,
                    35: 373.21,
                    40: 385.36
                }
                cost_by_m3 = cost_by_m3_dict[fck]
            except:
                raise Exception("Please, provide cost for concrete with {}MPa".format(fck))
            
        self.fck = fck
        self.cost_by_m3 = cost_by_m3
        self.material = Concrete(str(fck) + " MPa", aggressiveness, aggregate)
        self.biggest_aggregate_dimension = biggest_aggregate_dimension
        
        
        
def solve_cost(concrete_beam, decimal_numbers = 2):
    cost_table = [["Material", "Price", "Quantity", "Unit", "Commentary", "Is Subtotal"]]
    # Concrete
    total_concrete_cost = 0
    for beam_element in concrete_beam.initial_beam_elements:
        volume = beam_element.section.area*beam_element.length/1000000
        concrete_cost = volume*concrete_beam.available_concrete.cost_by_m3
        total_concrete_cost += concrete_cost
        row = ["Concrete",
                round(concrete_cost, decimal_numbers),
                round(volume, decimal_numbers), "m3", "Between {}m and {}m".format(beam_element.n1.x, beam_element.n1.x), False]
        cost_table = [*cost_table, row]
    row = ["Concrete", round(total_concrete_cost, 2), round(volume, 2), "m3", "", True]
    cost_table = [*cost_table, row]
    
    # Longitudinal
    total_long_bar_cost = total_length = 0
    for lb in concrete_beam.long_steel_bars:
        total_long_bar_cost += lb.cost
        total_length += lb.length
        row = ["Longitudinal bar",
            round(lb.cost, decimal_numbers),
            round(lb.length, decimal_numbers),
            "m",
            "Diameter {}mm. Between {}m and {}m".format(abs(lb.diameter*10),
                                                        round(lb.long_begin,decimal_numbers),
                                                        round(lb.long_end,decimal_numbers)),
            False]
        cost_table = [*cost_table, row]
        

    row = ["Longitudinal bar",
        round(total_long_bar_cost, decimal_numbers),
        round(total_length, decimal_numbers),
        "m", "", True]

    cost_table = [*cost_table, row]

    # Transversal Bar
    total_transv_bar_cost = total_length = 0
    for lb in concrete_beam.transv_steel_bars:
        total_transv_bar_cost += lb.cost
        total_length += lb.length
        row = ["Transversal bar",
            round(lb.cost, decimal_numbers),
            round(lb.length, decimal_numbers),
            "m",
            "{}cm x {}cm. Diameter {}mm. Placed in {}m ".format(round(lb.width,decimal_numbers),
                                                                round(lb.height,decimal_numbers),
                                                                abs(lb.diameter*10),
                                                                round(lb.x,decimal_numbers)), False]
        cost_table = [*cost_table, row]
        
    row = ["Transversal bar",
        round(total_transv_bar_cost, decimal_numbers),
        round(total_length, decimal_numbers),
        "m", "", True]

    cost_table = np.array([*cost_table, row])

    is_subtotal = cost_table[:, 5]
    is_subtotal = is_subtotal != "False"
    subtotal_table = cost_table[is_subtotal, :]

    return total_concrete_cost + total_transv_bar_cost + total_long_bar_cost, cost_table, subtotal_table