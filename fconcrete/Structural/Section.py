from fconcrete.helpers import cond, integrate, to_unit
import numpy as np
import matplotlib.pyplot as plt

class Section():
    """
    Class to represent simetrical section along the y axis.
    function_width is made to define the width along the y axis. The function starts with x=0 and ends in x=height.
    height is to represent the maximum y value possible.
    """    
    def __init__(self, function_width, height):
        height = to_unit(height, "cm").magnitude
        self.height = height
        self.function_width = function_width
        self.area = self.getAreaBetween(0, height, 1000)
        self.I = self._I()
        
        #self.bw = 2*min(abs(function_width))
        
    def width(self, height):
        return 0 if height>self.height else self.function_width(height)
    
    def getAreaBetween(self, begin_height, end_height, interations=100):
        return 2*integrate(self.function_width, begin_height, end_height, interations)
    
    def _I(self):
        raise NotImplementedError
        
    def plot(self, N=100):
        height = self.height
        x = np.linspace(0, height, N)
        
        y = np.linspace(0, height, N)
        x = np.array([self.function_width(xi) for xi in x])

        x_base = np.linspace(-x[0], x[0], 100)
        x_top = np.linspace(-x[-1], x[-1], 100)

        plt.plot(x, y) # plot right simetry
        plt.plot(2*y[0]-x, y) # plot left simetry
        plt.plot(x_base,np.zeros(len(y))) # plot base
        plt.plot(x_top,height*np.ones(len(y))) # plot top
        
        return
    
    
class Rectangle(Section):
    def __init__(self,width, height):
        width = to_unit(width, "cm").magnitude
        height = to_unit(height, "cm").magnitude
        self.__width = width
        self.height = height
        self.function_width = lambda x:width/2
        self.area = width*height
        self.I = self.width()*self.height**3/12
        self.bw = width
        self.y_cg = height/2
        
    def getAreaBetween(self, begin_height, end_height):
        return self.width()*(end_height - begin_height)
    
    def width(self, height=0):
        return self.__width