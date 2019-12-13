from fconcrete import Load, Node, ConcreteBeam, SingleBeamElement, Rectangle, Concrete, Section, ConcreteSteels

def test_structural_shear_diagram():
    material = Concrete(fck=30, aggressiveness=3)
    section = Rectangle(25,44.6, material)
    #E = 27000 I=1.8483
    f1 = Load.UniformDistributedLoad(-16.22/100, x_begin=0, x_end=113)
    f2 = Load.UniformDistributedLoad(-49.94/100, x_begin=113, x_end=113+470)
    f3 = Load.UniformDistributedLoad(-41.96/100, x_begin=113+470, x_end=113+470+605)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=113)
    n3 = Node.SimpleSupport(x=113+470)
    n4 = Node.SimpleSupport(x=113+470+605)

    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    bar3 = SingleBeamElement([n3, n4], section)

    beam = ConcreteBeam(
        loads = [f1, f2, f3],
        bars = [bar1, bar2, bar3],
        steel= ConcreteSteels(diameters=[8])
    )
    
    
    
    