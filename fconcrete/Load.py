import numpy as np

class Load:
    def __init__(self, force, momentum, x_begin, x_end, q=0, order=0):
        self.x = x_begin + (x_end-x_begin)/2
        self.x_begin = x_begin
        self.x_end = x_end
        self.force = force
        self.momentum = momentum
        self.q = q
        self.order = order
        
    @classmethod
    def PontualLoad(cls, force, x):
        return cls(force, 0, x, x, q=0, order=0)
    
    @classmethod
    def UniformDistributedLoad(cls, q, x_begin, x_end):
        return cls(q*(x_end-x_begin) , 0, x_begin, x_end, q=q, order=1)
        
    def __repr__(self):
        return str(self.__dict__)


class Loads:
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
        loads = np.array(loads)
        x_start = np.array([ load.x_begin for load in loads ])
        load_sort_position = np.argsort(x_start)
        return cls(loads[load_sort_position])
    
    
    def add(self, loads):
        loads = np.concatenate((self.loads,loads))
        return self.create(loads)
    
    def __repr__(self):
        return self.loads
     
    def __getitem__(self, key):
        return self.loads[key]
    
    def __len__(self):
        return len(self.loads)
    
