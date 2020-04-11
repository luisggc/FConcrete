from fconcrete.Structural import Material
from fconcrete.helpers import to_unit
from math import log

class Concrete(Material):
    """
        Define the Concrete to be used and all its properties.
        
        Attributes
        ----------
        fck : number
            Define the characteristic resistance of the concrete in kN/cmˆ2.
        
        E_ci : number
            Modulus of elasticity or initial tangent deformation module of concrete, always referring to the cordal module in kN/cmˆ2.
        
        E_cs : number
            Secant deformation module of concrete in kN/cmˆ2.
        
        fctm : number
            Average concrete tensile strength in kN/cmˆ2.
            
        fctk_inf : number
            Minimum value of direct tensile strength in kN/cmˆ2.
        
        fctk_sup : number
            Maximum value of direct tensile strength in kN/cmˆ2.
            
        fcd : number
            Minimum value of design direct tensile strength in kN/cmˆ2.

        c : number
            Concrete covering in cm.
        
        wk : number
            Characteristic crack opening in the concrete surface in cm.
    """
    def __init__(self, fck, aggressiveness, aggregate="granite"):
        """
            Define properties of the concrete.

                Call signatures:

                    fc.Concrete(fck, aggressiveness, aggregate='granite', **kwargs)

                >>> material = fc.Concrete(fck=30, aggressiveness=3)
                >>> round(material.fck)
                3

            Parameters
            ----------
            fck : number
                Define the characteristic resistance of the concrete.
                If it is a number, default unit is MPa, but also [force]/[length]**2 unit can be given. Example:
                '20kN/cm**2', '10Pa', etc
                
            aggressiveness : int
                Aggressiveness value from 1 (very low) to 4 (very height)

            aggregate : {'basalt', 'diabase', 'granite', 'gneiss', 'limestone', 'sandstone'}
                Aggregate type.
                
        """ 
        fck = to_unit(fck, "MPa")
        
        alpha_e = 0
        if aggregate in ['basalt', 'diabase']: alpha_e = 1.2
        if aggregate in ['granite', 'gneiss']: alpha_e = 1
        if aggregate in ["limestone"]: alpha_e = 0.9
        if aggregate in ["sandstone"]: alpha_e = 0.7
        if alpha_e == 0: raise Exception("Must select a valid aggregate: 'basalt', 'diabase', 'granite', 'gneiss', 'limestone' or 'sandstone'")
        
        if fck<20 or fck>90: raise Exception("Must select a valid fck value (between 20MPa and 90MPa)")
        if (fck>=20 and fck<=50): E_ci = alpha_e*5600*(fck**0.5)
        E_ci = alpha_e*21500*(fck/10+1.25)**(1/3) if fck>50 else E_ci
        alpha_i = min(0.8+0.2*fck/80, 1)
        E_cs = alpha_i*E_ci
        
        fctm = 0.3*(fck**(2/3)) if fck<=50 else 2.12*log(1+0.11*fck, 10)
        fctk_inf = 0.7*fctm
        fctk_sup = 1.3*fctm
        fcd = fck/1.4
        fctd = fctk_inf/1.4

        c = 2.5 if aggressiveness==1 else 3 if aggressiveness==2 else 4 if aggressiveness==3 else 5 if aggressiveness==4 else 0
        if c==0: raise Exception("Must select a valid aggressiveness value (between 1 and 4)")
        wk = 0.04 if aggressiveness==1 else 0.03 if aggressiveness in [2, 3] else 0.02 if aggressiveness==4 else 0
        
        self.fck = to_unit(fck, "MPa", "kN/cm**2")
        self.E_ci = to_unit(E_ci, "MPa", "kN/cm**2")
        self.E_cs = to_unit(E_cs, "MPa", "kN/cm**2")
        self.fctm = to_unit(fctm, "MPa", "kN/cm**2")
        self.fctk_inf = to_unit(fctk_inf, "MPa", "kN/cm**2")
        self.fctk_sup = to_unit(fctk_sup, "MPa", "kN/cm**2")
        self.fcd = to_unit(fcd, "MPa", "kN/cm**2")
        self.fctd = to_unit(fctd, "MPa", "kN/cm**2")
        self.c = c
        self.wk = wk
        self.aggressiveness = aggressiveness
        self.aggregate = aggregate
        
        Material.__init__(self, E_cs, 0.2, 10**(-5))