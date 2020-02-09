import numpy as np
from fconcrete.helpers import to_unit

class Load:
    """
        Class that defines a load.
    """
    def __init__(self, force, momentum, x_begin, x_end, q=0, order=0, displacement=0):
        force = to_unit(force, "kN")
        momentum = to_unit(momentum, "kNcm")
        x_begin = to_unit(x_begin, "cm")
        x_end = to_unit(x_end, "cm")
        q = to_unit(q, "kN/cm")
        
        self.x = x_begin + (x_end-x_begin)/2
        self.x_begin = x_begin
        self.x_end = x_end
        self.force = force
        self.momentum = momentum
        self.q = q
        self.order = order
        self.displacement = displacement
        
    @classmethod
    def PontualLoad(cls, load, x):
        """
            Define a pontual load.

                Call signatures:

                    fc.PontualLoad(load, x)

                >>> pontual_load_1 = fc.Load.PontualLoad(-10.0, 200)
                >>> pontual_load_2 = fc.Load.PontualLoad('-10.0kN', '2m')
                >>> repr(pontual_load_1) == repr(pontual_load_2)
                True

            Parameters
            ----------
            load : number or str
                Represent the load measure. If it is a number, default unit is kN, but also [force] unit can be given. Example:
                '20kN', '10N', etc
                
            x : number or str
                Where the load is going to end. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20cm', '10dm', etc
            
        """ 
        return cls(load, 0, x, x, q=0, order=0)
    
    @classmethod
    def UniformDistributedLoad(cls, q, x_begin, x_end):
        """
            Define a uniform and distributed load.

                Call signatures:

                    fc.UniformDistributedLoad(q, x_begin, x_end)

                >>> uniform_load_1 = fc.Load.UniformDistributedLoad(0.1, 0, 2000)
                >>> uniform_load_2 = fc.Load.UniformDistributedLoad('10.0kN/m', '0m', '20m')
                >>> repr(uniform_load_1) == repr(uniform_load_2)
                True

            Parameters
            ----------
            q : number or str
                Represent the load by length measure. If it is a number, default unit is kN/cm, but also [force]/[length] unit can be given. Example:
                '20kN/m', '10N/m', etc
                
            x_begin : number or str
                Where the load is going to start. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20cm', '10dm', etc
            
            x_end : number or str
                Where the load is going to end. If it is a number, default unit is cm, but also [length] unit can be given. Example:
                '20cm', '10dm', etc
        """ 
        
        q = to_unit(q, "kN/cm")
        x_begin = to_unit(x_begin, "cm")
        x_end = to_unit(x_end, "cm")
        force = q*(x_end-x_begin)
        
        return cls(force, 0, x_begin, x_end, q=q, order=1)
    
    #@classmethod
    # def DisplacementLoad(cls, x, displacement):
    #    return cls(0, 0, x, x, displacement=displacement)
    
    def __repr__(self):
        return str(self.__dict__)+'\n'


class Loads:
    """
        Class that defines a load list with easy to work properties and methods.
    """
    def __init__(self, loads):
        loads = np.array(loads)
        self.loads = loads
        self.x = np.array([ load.x for load in loads ])
        self.x_begin = np.array([ load.x_begin for load in loads ])
        self.x_end = np.array([ load.x_end for load in loads ])
        self.force = np.array([ load.force for load in loads ])
        self.momentum = np.array([ load.momentum for load in loads ])
        self.q = np.array([ load.q for load in loads ])
        self.order = np.array([ load.order for load in loads ])
    
    @classmethod
    def create(cls, loads):
        """
            Creates a instance of Loads with array of Load.
        """
        loads = np.array(loads)
        x_start = np.array([ load.x_begin for load in loads ])
        load_sort_position = np.argsort(x_start)
        return cls(loads[load_sort_position])
    
    
    def add(self, loads):
        """
            Add a array of Load in the Loads instance.
        """
        loads = np.concatenate((self.loads,loads))
        return self.create(loads)
    
    def __repr__(self):
        return str(self.loads)
     
    def __getitem__(self, key):
        return self.loads[key]
    
    def __len__(self):
        return len(self.loads)
    
