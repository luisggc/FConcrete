import numpy as np
from fconcrete import config as c
import matplotlib.pyplot as plt
import time

_Q = c._Q

def cond(x, singular=False, order=0):
    """
    If It is singular, return 1 if x>0 else 0.
    If It is not singular, return x**order if x>0 else 0
    """
    if singular:
        return 1 if x>0 else 0
    return x**order if x>0 else 0

def integrate(f, a, b, N=100):
    """
    Integrate f from a to b in N steps
    """
    x = np.linspace(a, b, N)
    y = np.apply_along_axis(f, 0, np.array([x]))
    return np.trapz(y, dx=(b-a)/(N-1))

def duplicated(array):
    """
    Check if it is duplicated.
    """
    s = np.sort(array, axis=None)
    duplicated = s[:-1][s[1:] == s[:-1]]
    return np.isin(s, duplicated)

def to_unit(input, expected_unit, return_unit=False):
    """
        Convert between unities according to expected_unit and return_unit

            Call signatures:

                fc.helpers.to_unit(input, expected_unit, return_unit=False)

            >>> fc.helpers.to_unit("10cm", "m")
            0.1
            >>> fc.helpers.to_unit(20, "m", return_unit="cm")
            2000
            
        Parameters
        ----------
        input: float or str
            Represents the input unit of the user.
        
        expected_unit: str
            The expected unit to be given. Useful when input is a number.
            
        return_unit: bool, optional
            The desired unit to return

        Returns
        -------
        Quantity
            The input in a clas that can have the unit easily manipulated.
    """
    try:
        input = float(input)
        value = _Q(input, expected_unit)
    except:
        pass
        try:
            value = _Q(input).to(expected_unit)
        except: raise Exception("String does not have valid format. See documentation.")
            
    if return_unit:
        return value.to(return_unit)
    return value
        
def getAxis(xy0=(0,0), xy1=(0,0)):
    """
    Create axis with equal aspect. xy0 and xy1 represent the visible area.
    """
    x0, y0 = xy0
    x1, y1 = xy1
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.plot([x0, x1], [y0, y1], color="None")
    return fig, ax

def timeit(do=True, name=""):
    """
    Decorator to print the time that the function has taken to execute.
    """
    def inner0(function):
        if not do: return function
        def inner(*args, **kw):
            start = time.time()
            val = function(*args, **kw)
            end = time.time()
            print("{} executed in {}s".format(function.__name__ if name == "" else name, end-start))
            return val
        return inner
    return inner0

# https://gist.github.com/snakers4/91fa21b9dda9d055a02ecd23f24fbc3d
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()