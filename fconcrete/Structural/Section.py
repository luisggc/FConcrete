from fconcrete.helpers import cond, integrate, to_unit, make_dxf
import numpy as np
import matplotlib.pyplot as plt
from fconcrete.helpers import getAxis

class Section():
    """
        Class to represent simetrical section along the y axis.
        
        Attributes
        ----------
        height : number
            Maximum height of the section in cm.
            
        function_width : function
            Define the width along the y axis. The function starts with x=0 and ends in x=height.
         
        area : number
            Total area of the section in cmˆ2.
        
        I : number
            Moment of inertia in cmˆ4.
            
        x0 : number
            Initial reference in the x axis.
            
        y0 : number
            Initial reference in the y axis.
    """    
    def __init__(self, function_width, height):
        """
            Creates simetrical section along the y axis.
            
            Parameters
            ----------
            function_width : function
                Define the width along the y axis. The function starts with x=0 and ends in x=height.
                
            height : number
                Represent the maximum y value possible in cm.
        """ 
        height = to_unit(height, "cm")
        self.height = height
        self.function_width = function_width
        self.area = self.getAreaBetween(0, height, 1000)
        self.I = self._I()
        self.x0, self.y0 = -self.function_width(0), 0
        #self.bw = 2*min(abs(function_width))
        
    def width(self, y):
        """
            Gets the width in y.
        """
        return 0 if y>self.height else self.function_width(y)
    
    def getAreaBetween(self, begin_height, end_height, interations=100):
        """
            Area between 2 y values.
        """
        return 2*integrate(self.function_width, begin_height, end_height, interations)
    
    def _I(self):
        raise NotImplementedError
        
    def plot(self, N=100, color_plot="red", ax=None, fig=None, **options):
        """
            Plot the section.
        """
        height = self.height
        
        fig, ax = getAxis() if ax == None else (fig, ax)
        y = np.linspace(0, height, N)
        x = np.array([self.function_width(xi) for xi in y])

        x_base = np.linspace(-x[0], x[0], 100)
        x_top = np.linspace(-x[-1], x[-1], 100)

        ax.plot(x, y, color=color_plot) # plot right simetry
        ax.plot(2*y[0]-x, y, color=color_plot) # plot left simetry
        ax.plot(x_base,np.zeros(len(y)), color=color_plot) # plot base
        ax.plot(x_top,height*np.ones(len(y)), color=color_plot) # plot top
        
        return make_dxf(ax, **options)
    
    
class Rectangle(Section):
    """
        Attributes
        ----------
        height : number
            Maximum height of the section in cm.
            
        function_width : function
            Define the width along the y axis. The function starts with x=0 and ends in x=height.
         
        bw : number
            Minimum width in cm.
        
        area : number
            Total area of the section in cmˆ2.
        
        I : number
            Moment of inertia in cmˆ4.
        
        y_cg : number
            Gravity center in the y axis.
        
        x0 : number
            Initial reference in the x axis.
            
        y0 : number
            Initial reference in the y axis.
    """
    def __init__(self,width, height):
        """
            Returns a concrete_beam element.
            
                Call signatures:

                    fc.Rectangle(width, height)

                >>> section = fc.Rectangle(25,56)
                
            Parameters
            ----------
            width : number
            height : number
        """    
        width = to_unit(width, "cm")
        height = to_unit(height, "cm")
        self.__width = width
        self.height = height
        self.function_width = lambda x:width/2
        self.area = width*height
        self.I = self.width()*self.height**3/12
        self.bw = width
        self.y_cg = height/2
        self.x0 = -width/2
        self.y0 = 0
        
    def getAreaBetween(self, begin_height, end_height):
        """
            Area between 2 y values.
        """
        return self.width()*(end_height - begin_height)
    
    def width(self, height=0):
        """
            Width value in cm.
        """
        return self.__width

    def __name__(self):
        return "Rectangle"
    
    
unitary_section = Rectangle(12, 10)
    