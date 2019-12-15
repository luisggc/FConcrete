import numpy as np

def cond(x, singular=False, order=0):
    if singular:
        return 1 if x>0 else 0
    return x**order if x>0 else 0

def integrate(f, a, b, N=100):
    x = np.linspace(a, b, N)
    #y = np.array([ f(xi) for xi in x ])
    y = np.apply_along_axis(f, 0, np.array([x]))
    return np.trapz(y, dx=(b-a)/(N-1))

def duplicated(array):
    s = np.sort(array, axis=None)
    duplicated = s[:-1][s[1:] == s[:-1]]
    return np.isin(s, duplicated)