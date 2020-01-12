import numpy as np
from fconcrete import config as c
import matplotlib.pyplot as plt
import time

_Q = c._Q

def cond(x, singular=False, order=0):
    if singular:
        return 1 if x>0 else 0
    return x**order if x>0 else 0

def integrate(f, a, b, N=100):
    x = np.linspace(a, b, N)
    y = np.apply_along_axis(f, 0, np.array([x]))
    return np.trapz(y, dx=(b-a)/(N-1))

def duplicated(array):
    s = np.sort(array, axis=None)
    duplicated = s[:-1][s[1:] == s[:-1]]
    return np.isin(s, duplicated)

def to_unit(input, expected_unit, return_unit=False):
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
    x0, y0 = xy0
    x1, y1 = xy1
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.plot([x0, x1], [y0, y1], color="None")
    return fig, ax

def timeit(do=True, name=""):
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