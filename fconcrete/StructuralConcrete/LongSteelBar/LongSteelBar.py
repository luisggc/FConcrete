import numpy as np
import matplotlib.pyplot as plt
import copy
from fconcrete.helpers import getAxis

class LongSteelBar():
    def __init__(self, long_begin, long_end, quantity, quantity_accumulated, diameter, area, area_accumulated, fyd, interspace, length, cost):
        self.long_begin = long_begin
        self.long_end = long_end
        self.quantity = quantity
        self.diameter = diameter
        self.interspace = interspace
        self.quantity_accumulated = quantity_accumulated
        self.area_accumulated = area_accumulated
        self.area = area
        self.fyd = fyd
        self.length = length
        self.cost = cost
    
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
        self.costs = np.array([ steel_bar.cost for steel_bar in self.steel_bars ])
        self.lengths = np.array([ steel_bar.length for steel_bar in self.steel_bars ])
        self.length = sum(self.lengths)
        self.cost = sum(self.costs)
        
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
    
    
    def getBarTransversalPosition(self, concrete_beam, x):
        
        _, beam_element = concrete_beam.getBeamElementInX(x)
        transversal_beam = concrete_beam.transv_steel_bars.getTransversalBarAfterX(x)
        material = beam_element.material
        section = beam_element.section
        distance_from_border = material.c+transversal_beam.diameter


        if len(self.steel_bars) == 0: return []
        
        transversal_positions = np.array([0,0,0,0])
        radius = max(abs(self.diameters))/2
        area = max(abs(self.areas))
        
        horizontal_distance = max(2, 2*radius, 1.2*concrete_beam.biggest_aggregate_dimension)
        vertical_distance = max(2, 2*radius, 0.5*concrete_beam.biggest_aggregate_dimension)

        x0, y0 = section.x0, section.y0
        x0_left_initial, x0_right_initial = x0+distance_from_border, -x0-distance_from_border
        x0_left, x0_right = x0_left_initial, x0_right_initial

        number_of_bars = max(abs(self.quantities_accumulated))
        is_positive_bar = self.areas_accumulated[0] > 0

        n, bar_in_the_left, row_number = 0, True, True

        while n<number_of_bars+1:
            #y_row = y0+beam_element.material.c+radius*(row_number+1)+(vertical_distance+radius)*(row_number-1)
            y_row = y0+distance_from_border+radius+(row_number-1)*(vertical_distance+radius)
            
            if bar_in_the_left:
                x_circle, y_circle = x0_left+radius, y_row if is_positive_bar else section.height-y_row
                x0_left+=2*radius+horizontal_distance
            else:
                x_circle, y_circle = x0_right-radius, y_row if is_positive_bar else section.height-y_row
                x0_right-=2*radius+horizontal_distance
            space_between_bars = x0_right-x0_left+2*horizontal_distance
            possible_bar_in_row = (space_between_bars+horizontal_distance)//(2*radius+horizontal_distance)
            # Nao tem espaco para colcoar nenhuma depois
            if possible_bar_in_row==0:
                row_number+=1
                x0_left = x0_left_initial
                x0_right = x0_right_initial
                bar_in_the_left = False
            else: 
                plot_center = (possible_bar_in_row==1 or n == number_of_bars) and bar_in_the_left
                point = (0, y_row if is_positive_bar else section.height-y_row) if plot_center else (x_circle, y_circle)
                transversal_positions = np.vstack((transversal_positions, (point[0], point[1], radius, area)))
            n+=1
            bar_in_the_left = not bar_in_the_left

        return transversal_positions[1:]


    def plotTransversal(self, concrete_beam, x, ax=None, fig=None, color_plot="red"):
        fig, ax = getAxis((-20,0), (20, 50)) if ax == None else (fig, ax)
        
        for long_bar in self.getBarTransversalPosition(concrete_beam, x):
            circle = plt.Circle((long_bar[0], long_bar[1]), long_bar[2])
            ax.add_artist(circle)
            
        return fig, ax # if return_ax else None
        
    
    def plot(self,prop='area_accumulated'):
        if prop=='area_accumulated':
            plt.gca().invert_yaxis()
            
        for steelbar in self.steel_bars:
            steelbar.plot(prop)
    
    def __getitem__(self, key):
        return self.steel_bars[key]
    
    def __repr__(self):
        return str(self.steel_bars)