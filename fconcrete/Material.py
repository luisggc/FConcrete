from fconcrete.helpers import to_unit
from math import log

class Material():
    """
        E - in MPA
        Poisson - 
    """    
    def __init__(self, E, poisson, alpha):
        self.E = E
        self.poisson = poisson
        self.alpha = alpha
        
class Concrete(Material):
    """
        Define properties of the concrete.

            Call signatures::

                Concrete(fck, aggressiveness, aggregate=granito, **kwargs)

            >>> Concrete(fck=30, aggressiveness=3)

        Parameters
        ----------
        fck : int
            Define the characteristic resistance of the concrete.
            If it is a number, default unit is MPa, but also [force]/[length]**2 unit can be give. Example:
            '20kN/cm**2', '10Pa', etc
            
        aggressiveness : int
            Aggressiveness value from 1 (very low) to 4 (very height)

        aggregate : str, optional
            Aggregate type. Options: basalto, diabásio, granito, gnaisse, calcário ou arenito.
            
        """ 
    def __init__(self, fck, aggressiveness, aggregate="granito"):
        fck = to_unit(fck, "MPa").magnitude
        
        alpha_e = 0
        if aggregate in ["basalto", "diabásio"]: alpha_e = 1.2
        if aggregate in ["granito", "gnaisse"]: alpha_e = 1
        if aggregate in ["calcário"]: alpha_e = 0.9
        if aggregate in ["arenito"]: alpha_e = 0.7
        if alpha_e == 0: raise Exception("Must select a valid aggregate: basalto, diabásio, granito, gnaisse, calcário ou arenito")
        
        if fck<20 or fck>90: raise Exception("Must select a valid fck value (between 20MPa and 90MPa)")
        if (fck>=20 and fck<=50): E_ci = alpha_e*5600*(fck**0.5)
        E_ci = alpha_e*21500*(fck/10+1.25)**(1/3) if fck>50 else E_ci
        
        # Check base for log expression
        fctm = 0.3*(fck**(2/3)) if fck<=50 else 2.12*log(1+0.11*fck, 10)
        fctk_inf = 0.7*fctm
        fctk_sup = 1.3*fctm
        fctd = fck/1.4

        c_in_cm = 2.5 if aggressiveness==1 else 3 if aggressiveness==2 else 4 if aggressiveness==3 else 5 if aggressiveness==4 else 0
        if c_in_cm==0: raise Exception("Must select a valid fck value (between 1 and 4)")
        
        self.fck = to_unit(fck, "MPa", "kN/cm**2").magnitude
        self.E_ci = to_unit(E_ci, "MPa", "kN/cm**2").magnitude
        self.fctm = to_unit(fctm, "kN/cm**2").magnitude
        self.fctk_inf = to_unit(fctk_inf, "kN/cm**2").magnitude
        self.fctk_sup = to_unit(fctk_sup, "kN/cm**2").magnitude
        self.fctd = to_unit(fctd, "kN/cm**2").magnitude
        self.c = c_in_cm
        
        super(Concrete, self ).__init__(E_ci, 0.2, 10**(-5))
    

        