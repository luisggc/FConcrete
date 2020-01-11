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
                 max_number=100,
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
                 fyw = 50,
                 max_number=3):
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
                 aggregate='granito'
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