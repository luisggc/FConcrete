from fconcrete.helpers import cond, integrate, to_unit
        
        
class Material():
    """
        Define the class for the material.
        
        Attributes
        ----------
        E : number
            Represent the Young Modulus (E) in kN/cmˆ2.
        
        poisson : number
            Poisson's ratio is a measure of the Poisson effect, that describes the expansion of a material in directions perpendicular to the direction of compression.
             
        alpha : number   
            Coefficient of thermal expansion which is the relative expansion (also called strain) divided by the change in temperature.
    """
    def __init__(self, E, poisson, alpha):
        """
            Define a material and its properties.

                Call signatures:

                    fc.Material(E, poisson, alpha)

                >>> generical_material = fc.Material(20000, 0.3, 10**(-6))
                >>> generical_material.E
                2000

            Parameters
            ----------
            E : number or str
                Represent the Young Modulus (E). If it is a number, default unit is kN/cmˆ2, but also [force]/[distance]**2 unit can be given. Example:
                '20000MPa', '10N/mmˆ2', etc
                
            poisson : number
                Poisson's ratio is a measure of the Poisson effect, that describes the expansion of a material in directions perpendicular to the direction of compression.
             
            alpha : number   
                Coefficient of thermal expansion which is the relative expansion (also called strain) divided by the change in temperature.
        """
        self.E = to_unit(E, "kN/cm**2")
        self.poisson = poisson
        self.alpha = alpha
    
unitary_material = Material(10**6, 1, 1)