import fconcrete as fc
import json

class API:
    """API is responsable to convert plain text to useful data."""
    def __init__(self, income_text):
        """Reiceive plain text and set attributes with useful data"""
        self.income_text = income_text
        self.status = "OK"
        try:
            concrete_beam_data = json.loads(income_text)["ConcreteBeam"]
            if concrete_beam_data:
                nodes = [self.getNode(node) for node in concrete_beam_data["nodes"]]
                loads = [self.getLoad(load) for load in concrete_beam_data["loads"]]
                width, height = concrete_beam_data["section"]["width"], concrete_beam_data["section"]["height"]
                other_parameters = { k:v for (k, v) in concrete_beam_data.items() if not k in ["nodes", "loads", "section"]}
                
                concrete_beam = fc.ConcreteBeam(
                        loads = loads,
                        nodes = nodes,
                        section = fc.Rectangle(width,height),
                        **other_parameters
                )
            self.concrete_beam = concrete_beam
        except Exception as excep:
            error = str(excep)
            self.status = error
            
    @staticmethod
    def getNode(noad_dict):
        if noad_dict["type"] == "Free" :
            return getattr(fc.Node, noad_dict["type"])(x=noad_dict["x"])
        return getattr(fc.Node, noad_dict["type"])(x=noad_dict["x"], length=noad_dict["length"])
        
    @staticmethod
    def getLoad(load_dict):
            if load_dict["type"] == "UniformDistributedLoad":
                return fc.Load.UniformDistributedLoad(x_begin=load_dict["x_begin"], x_end=load_dict["x_end"], q=load_dict["q"])
            if load_dict["type"] == "PontualLoad":
                return fc.Load.PontualLoad(x=load_dict["x"], load=load_dict["load"])
            
    def __repr__(self):
        return self.income_text



    