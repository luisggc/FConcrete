import numpy as np
import matplotlib.pyplot as plt
import copy

class LongSteelBar():
    def __init__(self, long_begin, long_end, quantity, quantity_accumulated, diameter, area, area_accumulated, fyd, interspace):
        self.long_begin = long_begin
        self.long_end = long_end
        self.quantity = quantity
        self.diameter = diameter
        self.interspace = interspace
        self.quantity_accumulated = quantity_accumulated
        self.area_accumulated = area_accumulated
        self.area = area
        self.fyd = fyd
    
    @staticmethod
    def getSteelArea(section, material, steel, momentum):
        b = section.width()
        d = section.d
        if momentum==0: return 0
        kc = b*d**2/momentum
        if (kc<1.5 and kc>-1.5): raise Exception('Momentum too high to section')
        fyd = steel.fyd
        fcd = material.fcd
        beta_x = (1-(1-1.6/(0.68*fcd*kc))**(0.5))/0.8
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
    
        
    def plot(self,prop='area_accumulated'):
        y = getattr(self, prop)
        plt.plot([self.long_begin, self.long_end], [y,y])
    
    def __repr__(self):
        return str(self.__dict__)+'\n'
    
    
class LongSteelBars():
    def __init__(self, steel_bars=[]):
        self.steel_bars = np.array(steel_bars)
        self.long_begins = np.array([ steel_bar.long_begin for steel_bar in self.steel_bars ])
        self.long_ends = np.array([ steel_bar.long_end for steel_bar in self.steel_bars ])
        self.quantities = np.array([ steel_bar.quantity for steel_bar in self.steel_bars ])
        self.diameters = np.array([ steel_bar.diameter for steel_bar in self.steel_bars ])
        self.interspaces = np.array([ steel_bar.interspace for steel_bar in self.steel_bars ])
        self.quantities_accumulated = np.array([ steel_bar.quantity_accumulated for steel_bar in self.steel_bars ])
        self.areas_accumulated = np.array([ steel_bar.area_accumulated for steel_bar in self.steel_bars ])
        self.areas = np.array([ steel_bar.area for steel_bar in self.steel_bars ])
        self.fyds = np.array([ steel_bar.fyd for steel_bar in self.steel_bars ])
        
    def add(self, new_steel_bars):
        previous_steel_bars = self.steel_bars
        if str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.LongSteelBar.LongSteelBar.LongSteelBars'>":
            concatenation = list(np.concatenate((previous_steel_bars,new_steel_bars.steel_bars)))
            concatenation.sort(key=lambda x: x.long_begin, reverse=False)
            new_steel_bars = np.array(concatenation)
            
        elif str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.LongSteelBar.LongSteelBar.LongSteelBar'>":
            new_steel_bars = np.append(previous_steel_bars,new_steel_bars)
        self.__init__(new_steel_bars)
    
    def changeProperty(self, prop, function, conditional=lambda x:True):
        steel_bars = copy.deepcopy(self)
        for previous_steel_bar in steel_bars:
            if conditional(previous_steel_bar):
                current_attribute_value = getattr(previous_steel_bar, prop)
                setattr(previous_steel_bar, prop, function(current_attribute_value)) 
        return LongSteelBars(steel_bars.steel_bars)

    def getPositiveandNegativeLongSteelBarsInX(self, x):
        positive_steel_bar_in_x = np.array([steel_bar if condition else None 
                               for condition, steel_bar
                               in zip((self.long_begins<=x) & (self.long_ends>=x) & (self.areas>0), self.steel_bars)])

        negative_steel_bar_in_x = np.array([steel_bar if condition else None 
                                for condition, steel_bar
                                in zip((self.long_begins<=x) & (self.long_ends>=x) & (self.areas<0), self.steel_bars)])
        
        positive_steel_bar_in_x = LongSteelBars(positive_steel_bar_in_x[positive_steel_bar_in_x!=None])
        negative_steel_bar_in_x = LongSteelBars(negative_steel_bar_in_x[negative_steel_bar_in_x!=None])
        return positive_steel_bar_in_x, negative_steel_bar_in_x
        
    def plot(self,prop='area_accumulated'):
        if prop=='area_accumulated':
            plt.gca().invert_yaxis()
            
        for steelbar in self.steel_bars:
            steelbar.plot(prop)
    
    def __getitem__(self, key):
        return self.steel_bars[key]
    
    def __repr__(self):
        return str(self.steel_bars)