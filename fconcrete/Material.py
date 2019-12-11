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

                Concrete(fck_in_mpa, aggressiveness, aggregate=granito, **kwargs)

            >>> Concrete(fck=30, aggressiveness=3)

        Parameters
        ----------
        fck_in_mpa : int
            Define, in MPa (10^6 N/m²), the characteristic resistance of the concrete.
            
        aggressiveness : int
            Aggressiveness value from 1 (very low) to 4 (very height)

        aggregate : str, optional
            Aggregate type. Options: basalto, diabásio, granito, gnaisse, calcário ou arenito.
            
        """ 
    def __init__(self, fck_in_mpa, aggressiveness, aggregate="granito"):
        alpha_e = 0
        if aggregate in ["basalto", "diabásio"]: alpha_e = 1.2
        if aggregate in ["granito", "gnaisse"]: alpha_e = 1
        if aggregate in ["calcário"]: alpha_e = 0.9
        if aggregate in ["arenito"]: alpha_e = 0.7
        if alpha_e == 0: raise Exception("Must select a valid aggregate: basalto, diabásio, granito, gnaisse, calcário ou arenito")
        
        fck = fck_in_mpa
        if fck<20 or fck>90: raise Exception("Must select a valid fck value (between 20MPa and 90MPa)")
        if (fck>=20 and fck<=50): E_ci = alpha_e*5600*(fck**0.5)
        E_ci = alpha_e*21500*(fck/10+1.25)**(1/3) if fck>50 else E_ci
            
        fctm = 0.3*(fck**(2/3)) if fck<=50 else 2.12*log(1+0.11*fck)
        fctk_inf = 0.7*fctm
        fctk_sup = 1.3*fctm
        fctd = fck/1.4

        self.c = 0.025 if aggressiveness==1 else 0.03 if aggressiveness==2 else 0.04 if aggressiveness==3 else 0.05 if aggressiveness==4 else 0
        if self.c==0: raise Exception("Must select a valid fck value (between 1 and 4)")
        
        super(Concrete, self ).__init__(E_ci, 0.2, 10**(-5))
        
        self.fck = fck
        self.E_ci = E_ci
        self.fctm = fctm
        self.fctk_inf = fctk_inf
        self.fctk_sup = fctk_sup
        self.fctd = fctd
    

        