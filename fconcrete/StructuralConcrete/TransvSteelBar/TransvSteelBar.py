import numpy as np
import matplotlib.pyplot as plt
import copy
from fconcrete.helpers import getAxis, make_dxf

class TransvSteelBar():
    def __init__(self, x, height, width, diameter, space_after, area, as_per_cm, anchor, length, cost):
        self.x = x
        self.height = height
        self.width = width
        self.diameter = diameter
        self.space_after = space_after
        self.area = area
        self.as_per_cm = as_per_cm
        self.anchor = anchor
        self.length = length
        self.cost =  cost
        
    def __repr__(self):
        return str(self.__dict__)+'\n'
    
    def plot(self, c=2, ax=None, fig=None, color_plot="blue", **options):
        """
            Plot the transversal vision of the transversal bar.
        """
        height, width, diameter = self.height, self.width, self.diameter
        x0, y0 = -width/2, c
        
        fig, ax = getAxis((x0, diameter), (x0+diameter+width-diameter, c+height)) if ax == None else (fig, ax)
        
        left_bar = plt.Rectangle((x0,y0), diameter, height, hatch="/", fill=False)
        right_bar = plt.Rectangle((width/2-diameter,y0), diameter, height, hatch="/", fill=False)
        top_bar = plt.Rectangle((x0+diameter,y0+height-diameter), width-2*diameter, diameter, hatch="/", fill=False)
        bottom_bar = plt.Rectangle((x0+diameter,y0), width-2*diameter, diameter, hatch="/", fill=False)
        anchor = plt.Rectangle((width/2+diameter/2, y0+height-diameter/2), diameter, self.anchor, hatch="|", fill=False, angle=135) #anchor

        ax.add_artist(left_bar)
        ax.add_artist(right_bar)
        ax.add_artist(top_bar)
        ax.add_artist(bottom_bar)
        ax.add_artist(anchor)

        return make_dxf(ax, **options) # if return_ax else None
        

class TransvSteelBars():
    """
        Class that defines a the TransvSteelBar list with easy to work properties and methods.
    """
    def __init__(self, steel_bars=[]):
        self.steel_bars = np.array(steel_bars)
        self.x = np.array([ steel_bar.x for steel_bar in self.steel_bars ])
        self.heights = np.array([ steel_bar.height for steel_bar in self.steel_bars ])
        self.widths = np.array([ steel_bar.width for steel_bar in self.steel_bars ])
        self.diameters = np.array([ steel_bar.diameter for steel_bar in self.steel_bars ])
        self.space_afters = np.array([ steel_bar.space_after for steel_bar in self.steel_bars ])
        self.areas = np.array([ steel_bar.area for steel_bar in self.steel_bars ])
        self.as_per_cms = np.array([ steel_bar.as_per_cm for steel_bar in self.steel_bars ])
        self.lengths = np.array([ steel_bar.length for steel_bar in self.steel_bars ])
        self.costs = np.array([ steel_bar.cost for steel_bar in self.steel_bars ])
        self.length = sum(self.lengths)
        self.cost = sum(self.costs)

    def add(self, new_steel_bars):
        """
            Add a array of Load in the Loads instance.
        """
        previous_steel_bars = self.steel_bars
        if str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.TransvSteelBar.TransvSteelBar.TransvSteelBars'>":
            concatenation = list(np.concatenate((previous_steel_bars,new_steel_bars.steel_bars)))
            concatenation.sort(key=lambda x: x.long_begin, reverse=False)
            new_steel_bars = np.array(concatenation)
            
        elif str(type(new_steel_bars)) == "<class 'fconcrete.StructuralConcrete.TransvSteelBar.TransvSteelBar.TransvSteelBar'>":
            new_steel_bars = np.append(previous_steel_bars,new_steel_bars)
        self.__init__(new_steel_bars)
    
    def getTransversalBarAfterX(self, x):
        """
            Get the next transversal bar in x or after.
        """
        return self.steel_bars[self.x >= x][0]
    
    def changeProperty(self, prop, function, conditional=lambda x:True):
        """
            Change all properties of the TransvSteelBar in a single function.
        """
        steel_bars = copy.deepcopy(self)
        for previous_steel_bar in steel_bars:
            if conditional(previous_steel_bar):
                current_attribute_value = getattr(previous_steel_bar, prop)
                setattr(previous_steel_bar, prop, function(current_attribute_value)) 
        return steel_bars

    def plotLong(self, **options):
        """
            Plot the longitudinal vision of the transversal bar.
        """
        _, ax = plt.subplots()
        for x, height in zip(self.x, self.heights):
            ax.plot([x,x], [0,height])
        return make_dxf(ax, **options)
            
    def __getitem__(self, key):
        return self.steel_bars[key]
    
    def __repr__(self):
        return str(self.steel_bars)