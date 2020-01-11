from fconcrete.helpers import cond, integrate, to_unit
        
        
class Material():
    """
        E - in MPA
        Poisson - 
    """    
    def __init__(self, E, poisson, alpha):
        self.E = to_unit(E, "MPa", "kN/cm**2").magnitude
        self.poisson = poisson
        self.alpha = alpha
    
unitary_material = Material(10**6, 1, 1)