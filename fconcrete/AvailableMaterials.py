import numpy as np

class AvailableConcreteSteelBar:
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
                 fyd = 50/1.15,
                 max_number=100):
        try:
            areas = [diameters_to_area[diameter] for diameter in diameters]
        except:
            raise Exception("Must provide a valid diameter to area dict")
            
        diameters = np.array(diameters)
        areas = np.array(areas)
        diameters_loop = np.tile(diameters/10, max_number-1)
        areas_loop = np.concatenate([ areas*(i) for i in range(2, max_number+1)])
        number_of_bars = areas_loop/np.tile(areas,max_number-1)
        table_of_positive_steel = np.stack((number_of_bars, diameters_loop, areas_loop), axis=1)
        table_of_negative_steel = -np.array(table_of_positive_steel)
        table_of_positive_and_negative_steel = np.vstack([table_of_negative_steel, table_of_positive_steel])
        table = np.array(table_of_positive_and_negative_steel[
            table_of_positive_and_negative_steel[:,2].argsort()
        ])
        self.table = table
        self.fyd = fyd
    
    
    
        