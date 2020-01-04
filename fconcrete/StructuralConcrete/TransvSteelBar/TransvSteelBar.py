import numpy as np
import matplotlib.pyplot as plt
import copy

class TransvSteelBar():
    def __init__(self, x, height, width, diameter, space_after, area, as_per_cm):
        self.x = x
        self.height = height
        self.width = width
        self.diameter = diameter
        self.space_after = space_after
        self.area = area
        self.as_per_cm = as_per_cm
    
    def __repr__(self):
        return str(self.__dict__)+'\n'

class TransvSteelBars():
    def __init__(self, steel_bars=[]):
        self.steel_bars = np.array(steel_bars)
        self.x = np.array([ steel_bar.x for steel_bar in self.steel_bars ])
        self.heights = np.array([ steel_bar.height for steel_bar in self.steel_bars ])
        self.widths = np.array([ steel_bar.width for steel_bar in self.steel_bars ])
        self.diameters = np.array([ steel_bar.diameter for steel_bar in self.steel_bars ])
        self.space_afters = np.array([ steel_bar.space_after for steel_bar in self.steel_bars ])
        self.areas = np.array([ steel_bar.area for steel_bar in self.steel_bars ])
        self.as_per_cms = np.array([ steel_bar.as_per_cm for steel_bar in self.steel_bars ])
    
    def add(self, new_steel_bars):
        previous_steel_bars = self.steel_bars
        if str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.TransvSteelBar.TransvSteelBar.TransvSteelBars'>":
            concatenation = list(np.concatenate((previous_steel_bars,new_steel_bars.steel_bars)))
            concatenation.sort(key=lambda x: x.long_begin, reverse=False)
            new_steel_bars = np.array(concatenation)
            
        elif str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.TransvSteelBar.TransvSteelBar.TransvSteelBar'>":
            new_steel_bars = np.append(previous_steel_bars,new_steel_bars)
        self.__init__(new_steel_bars)
    
    def changeProperty(self, prop, function, conditional=lambda x:True):
        steel_bars = copy.deepcopy(self)
        for previous_steel_bar in steel_bars:
            if conditional(previous_steel_bar):
                current_attribute_value = getattr(previous_steel_bar, prop)
                setattr(previous_steel_bar, prop, function(current_attribute_value)) 
        return steel_bars

    def plotLong(self):
        for x, height in zip(self.x, self.heights):
            plt.plot([x,x], [0,height])
            
    def __getitem__(self, key):
        return self.steel_bars[key]
    
    def __repr__(self):
        return str(self.steel_bars)