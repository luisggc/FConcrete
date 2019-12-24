import numpy as np

class AvailableConcreteSteels:
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
    
    @staticmethod
    def getSteelArea(section, material, steel, momentum):
        b = section.width()
        d = section.d
        if momentum==0: return 0
        kc = b*d**2/momentum
        if (kc<1.5 and kc>-1.5): raise Exception('Momentum too high to section')
        fyd = steel.fyd
        fctd = material.fctd
        beta_x = (1-(1-1.6/(0.68*fctd*kc))**(0.5))/0.8
        tension_steel = np.where((beta_x <= 0.28) or (3.5*(beta_x**(-1)-1)*20>fyd), fyd, 3.5*(beta_x**(-1)-1)*20)+0
        ks = (tension_steel*(1-0.4*beta_x))**(-1)
        As = ks*momentum/d
        return As
    
    @staticmethod
    def getMinimumAndMaximumSteelArea(area, fck):
        fck_array = 20 + 5*np.arange(15)
        p_min_array = np.array([ 0.15, 1.15, 1.15, 1.164, 0.179, 0.194, 0.208, 0.211, 0.219, 0.226, 0.233, 0.239, 0.245, 0.251, 0.256])
        p_min = np.interp(fck, fck_array, p_min_array)
        A_min = area*p_min/100
        A_max = 0.008*area
        return A_min, A_max
    
        