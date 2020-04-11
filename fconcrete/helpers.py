import numpy as np
from fconcrete import config as c
import matplotlib.pyplot as plt
import time
import ezdxf
import pandas as pd

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
        Convert between unities according to expected_unit and return_unit.

            Call signatures:

                fc.helpers.to_unit(input, expected_unit, return_unit=False)

            >>> unit1 = fc.helpers.to_unit("10cm", "m")
            >>> unit1
            0.1
            
            >>> unit2 = fc.helpers.to_unit(20, "m", return_unit="cm")
            >>> unit2
            2000.0
            
        Parameters
        ----------
        input : number or str
            Represents the input unit of the user.
        
        expected_unit : str
            The expected unit to be given. Useful when input is a number.
            
        return_unit : `bool`, optional
            The desired unit to return

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
        return value.to(return_unit).magnitude
    return value.magnitude
        
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
        
def make_dxf(ax, **options):
    """
        Matplotlib graph to modelspace (preparation to dxf).
        Returns ax and msp.
    """
    msp = options["msp"] if options.get("msp") else False
    scale_y = options["scale_y"] if options.get("scale_y") else 1
    scale_x = options["scale_x"] if options.get("scale_x") else 1
    xy_position = options["xy_position"] if options.get("xy_position") else (0,0)
    
    if msp == False:
        doc = ezdxf.new('AC1032')
        doc.header['$INSUNITS'] = 5
        msp = doc.modelspace()
        
    for element in ax.get_children():
        element_type = str(type(element))
        if element_type == "<class 'matplotlib.lines.Line2D'>":
            xy_data = element.get_xydata()
            xy_data[:, 1] = xy_data[:, 1]*scale_y
            xy_data[:, 0] = xy_data[:, 0]*scale_x
            points = xy_data[np.invert(np.isnan(xy_data[:, 1]))]+xy_position
            msp.add_lwpolyline(points)
        elif element_type == "<class 'matplotlib.patches.Rectangle'>":
            #p1, p2 = element.get_bbox().get_points()
            points = element.get_patch_transform().transform(element.get_path().vertices[:-1]) #np.array([p1, [p1[0], p2[1]], p2, [p2[0], p1[1]], p1])
            points = np.array([*points, points[0]])+xy_position
            msp.add_lwpolyline(points)
            if element.get_hatch():
                hatch = msp.add_hatch()
                hatch.set_pattern_fill('ANSI31', scale=0.5, angle=element.angle)
                hatch.paths.add_polyline_path(points, is_closed=1)
        elif element_type == "<class 'matplotlib.patches.Circle'>":
            msp.add_circle(np.array(element.center)+xy_position, element.radius)
    
    return ax, msp

def to_pandas(array_table):
    df_table = pd.DataFrame(array_table)
    df_table.columns = df_table.iloc[0]
    df_table = df_table.drop(df_table.index[0])
    return df_table
