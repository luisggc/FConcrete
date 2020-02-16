from fconcrete.Structural.Section import Section

class ConcreteSection(Section):
    """
        Inject ConcreteSection properties to a generic Section.
    """
        
    @staticmethod
    def setSteelHeight(
        section,
        positive_steel_height = 0,
        negative_steel_height = 0
    ):
        """
            Inject steel height (d) to the section.
        """
        if (positive_steel_height == 0 and negative_steel_height==0):
            p, n = section.height*0.8, section.height*0.8
            minimum, maximum = min(p, n), max(p, n)
        elif(positive_steel_height == 0 or negative_steel_height == 0):
            p = positive_steel_height if positive_steel_height else 0
            n = negative_steel_height if negative_steel_height else 0
            maximum = minimum = p + n
        else:
            p, n = positive_steel_height, negative_steel_height
            minimum, maximum = min(p, n), max(p, n)
            
        section.positive_steel_height = p
        section.negative_steel_height = n
        section.maximum_steel_height = maximum
        section.minimum_steel_height = minimum
        
        return section