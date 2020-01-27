import numpy as np
from math import sin, tan,  pi
from fconcrete.StructuralConcrete.Concrete import Concrete

#https://loja.arcelormittal.com.br/vergalhao-ca50-soldavel-63mm/p
class AvailableLongConcreteSteelBar:
    def __init__(self,
                 diameters=[6.3, 8, 10, 12.5, 16, 20, 25, 32],
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
                 fyw = 50/1.15,
                 E = 21000,
                 max_number=200,
                 surface_type="ribbed"):
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
    def __init__(self,
                 diameters=[6.3, 8, 10, 12.5, 16, 20, 25, 32],
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
                 fyw = 50):
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
    
#https://servicos.compesa.com.br/wp-content/uploads/2016/02/TABELA_COMPESA_2016_SEM_DESONERACAO_E_SEM_ENCARGOS_COMPLEMENTARES.pdf
class AvailableConcrete():
    def __init__(self,
                 fck=30,
                 cost_by_m3=None,
                 aggressiveness=3,
                 aggregate='granite'
                 ):
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