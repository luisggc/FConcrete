import numpy as np
from math import sin, tan,  pi

class AvailableLongConcreteSteelBar:
    def __init__(self,
                 diameters=[5, 6.3, 8, 10, 12.5, 16, 20, 25, 32, 40],
                 diameters_to_area={
                        5: 0.2,
                        6.3: 0.315,
                        8: 0.5,
                        10: 0.8,
                        12.5: 1.25,
                        16: 2,
                        20: 3.15,
                        25: 5,
                        32: 8,
                        40: 12.5
                    },
                 fyw = 50/1.15,
                 max_number=100,
                 steel_bar_surface_type="ribbed"):
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
        
        table_of_negative_steel = np.stack((number_of_bars, -diameters_loop, -areas_loop), axis=1)
        table_of_positive_and_negative_steel = np.vstack([table_of_negative_steel, table_of_positive_steel])
        
        table = np.array(table_of_positive_and_negative_steel[
            table_of_positive_and_negative_steel[:,2].argsort()
        ])
        self.table = table
        self.fyw = fyw
        self.fyd = fyd
        self.diameters = diameters
        self.diameters_to_area = diameters_to_area
        self.steel_bar_surface_type = steel_bar_surface_type
        
        
class AvailableTransvConcreteSteelBar:
    def __init__(self,
                 diameters=[5, 6.3, 8, 10, 12.5, 16, 20, 25, 32, 40],
                 diameters_to_area={
                        5: 0.2,
                        6.3: 0.315,
                        8: 0.5,
                        10: 0.8,
                        12.5: 1.25,
                        16: 2,
                        20: 3.15,
                        25: 5,
                        32: 8,
                        40: 12.5
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
        diameters_loop = np.tile(diameters, len(possible_spaces))
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
    
    
        