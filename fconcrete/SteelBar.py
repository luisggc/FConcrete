import numpy as np
import matplotlib.pyplot as plt
import fconcrete
print("entrou")
class SteelBar():
    def __init__(self, long_begin, long_end, quantity, diameter):
        available_steel = fconcrete.config.available_material['concrete_steel_bars']
        self.long_begin = long_begin
        self.long_end = long_end
        self.quantity = quantity
        self.diameter = diameter
        self.area = available_steel.diameters_to_area[abs(diameter*10)]*quantity*(1 if diameter>0 else -1)
    
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
    
        
    def plot(self,prop='quantity'):
        y = getattr(self, prop)
        plt.plot([self.long_begin, self.long_end], [y,y])
    
    def __repr__(self):
        return str(self.__dict__)+'\n'
    
    
class SteelBars():
    def __init__(self, steel_bars=[]):
        self.steel_bars = np.array(steel_bars)
    
    def add(self, steelbar):
        if str(type(steelbar)) == "<class 'fconcrete.SteelBar.SteelBars'>":
            concatenation = list(np.concatenate((self.steel_bars,steelbar.steel_bars)))
            concatenation.sort(key=lambda x: x.long_begin, reverse=False)
            self.steel_bars = np.array(concatenation)
            
        elif str(type(steelbar)) == "<class 'fconcrete.SteelBar.SteelBar'>":
            self.steel_bars = np.append(self.steel_bars,steelbar)
    
    def plot(self,prop='quantity'):
        for steelbar in self.steel_bars:
            steelbar.plot(prop)
    
    def __getitem__(self, key):
        return self.steel_bars[key]
    
    def __repr__(self):
        return str(self.steel_bars)