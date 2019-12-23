from fconcrete import duplicated, e, Material, Beam, Load, Node, ConcreteBeam, SingleBeamElement, Rectangle, Concrete, Section, ConcreteSteels
from pytest import approx
import numpy as np
import os

def approx01(x):
    return approx(x, abs=0.1)

def create_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-1, x=500)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=1000)
    bar1 = SingleBeamElement([n1, n2], section)
    return Beam(
        loads = [f1],
        bars = [bar1],
        solve_structural=False
    )
    
def create_simple_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-1, x=500)
    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=1000)
    bar1 = SingleBeamElement([n1, n2], section)
    return Beam(
        loads = [f1],
        bars = [bar1],
        solve_structural=False
    )
    
def test_structural_create_simple_beam():
    beam = create_simple_beam()
    assert beam.solve_structural() == None
    

def test_structural_create_crimped_beam():
    beam = create_crimped_beam()
    assert beam.solve_structural() == None

def test_structural_simple_beam():
    beam = create_simple_beam()
    beam.solve_structural()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(0.5)
    assert support_reaction[1] == approx(0)
    assert support_reaction[-2] == approx(0.5)
    assert support_reaction[-1] == approx(0)
    assert beam.getInternalMomentumStrength(beam.length/2) == approx(1*1000/4)
    assert beam.getInternalShearStrength(beam.length/2-e) == approx(0.5)
    assert beam.getInternalShearStrength(beam.length/2+e) == approx(-0.5)
    
def test_structural_crimped_beam():
    beam = create_crimped_beam()
    beam.solve_structural()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(0.5)
    assert support_reaction[1] == approx(1*1000/8)
    assert support_reaction[-2] == approx(0.5)
    assert support_reaction[-1] == approx(-1*1000/8)
    assert beam.getInternalShearStrength(beam.length/2-e) == approx(0.5)
    assert beam.getInternalShearStrength(beam.length/2+e) == approx(-0.5)
    assert beam.getInternalMomentumStrength(e) == approx(-1*1000/8, abs=1)
    assert beam.getInternalMomentumStrength(beam.length-e) == approx(-1*1000/8, abs=1)
    assert beam.getInternalMomentumStrength(beam.length/2) == approx(-1*1000/8+0.5*500, abs=1)
    
def test_structural_double_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=200)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=1000)
    bar1 = SingleBeamElement([n1, n2], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1]
    )
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(179.2, abs=0.1)
    assert support_reaction[1] == approx(25600, abs=10)
    assert support_reaction[-2] == approx(20.8, abs=0.1)
    assert support_reaction[-1] == approx(-6400, abs=10)
    assert beam.getInternalShearStrength(150) == approx(179.2, abs=0.1)
    assert beam.getInternalShearStrength(300) == approx(-20.8, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-25600, abs=10)
    assert beam.getInternalMomentumStrength(200) == approx(+10240, abs=10)
    assert beam.getInternalMomentumStrength(170) == approx(4860, abs=10)
    assert beam.getInternalMomentumStrength(210) == approx(10030, abs=10)
    assert beam.getInternalMomentumStrength(1000-e) == approx(-6400, abs=10)
    
def test_structural__crimped_simple_supported_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    bar1 = SingleBeamElement([n1, n2], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1]
    )
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(87.3, abs=0.1)
    assert support_reaction[1] == approx(27300, abs=10)
    assert support_reaction[-2] == approx(112.7, abs=0.1)
    assert support_reaction[-1] == approx(0, abs=10)
    assert beam.getInternalShearStrength(100) == approx(87.3, abs=0.1)
    assert beam.getInternalShearStrength(800) == approx(-112.7, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-27300, abs=10)
    assert beam.getInternalMomentumStrength(100) == approx(-18570, abs=10)
    assert beam.getInternalMomentumStrength(800) == approx(+22540, abs=10)
    assert beam.getInternalMomentumStrength(1000-e) == approx(0, abs=10)
    
def test_structural__crimped_simplesupported_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    n3 = Node.Crimp(x=1500)
    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1, bar2],
    )
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(57.9, abs=0.1)
    assert support_reaction[1] == approx(17500, abs=10)
    assert support_reaction[-4] == approx(200.9, abs=0.1)
    assert support_reaction[-3] == approx(0, abs=10)
    assert support_reaction[-2] == approx(-58.8, abs=0.1)
    assert support_reaction[-1] == approx(9800, abs=10)
    
    assert beam.getInternalShearStrength(100) == approx(57.9, abs=0.1)
    assert beam.getInternalShearStrength(800) == approx(-142.1, abs=0.1)
    assert beam.getInternalShearStrength(1200) == approx(58.8, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-17500, abs=1)
    assert beam.getInternalMomentumStrength(100) == approx(-11710, abs=1)
    assert beam.getInternalMomentumStrength(800) == approx(8820, abs=1)
    assert beam.getInternalMomentumStrength(1200) == approx(-7840, abs=1)
    assert beam.getInternalMomentumStrength(1500-e) == approx(9800, abs=1)
    
def test_structural__crimped_simplesupported_simplesupported_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    n3 = Node.SimpleSupport(x=1500)
    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1, bar2],
    )
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(60.8, abs=0.1)
    assert support_reaction[1] == approx(18480, abs=0.1)
    assert support_reaction[-4] == approx(174.4, abs=0.1)
    assert support_reaction[-3] == approx(0, abs=0.1)
    assert support_reaction[-2] == approx(-35.30, abs=10)
    assert support_reaction[-1] == approx(0, abs=0.1)
    
    assert beam.getInternalShearStrength(100) == approx(60.8, abs=0.1)
    assert beam.getInternalShearStrength(800) == approx(-139.2, abs=0.1)
    assert beam.getInternalShearStrength(1200) == approx(35.3, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-18480, abs=1)
    assert beam.getInternalMomentumStrength(100) == approx(-12400, abs=10)
    assert beam.getInternalMomentumStrength(800) == approx(10190, abs=10)
    assert beam.getInternalMomentumStrength(1200) == approx(-10580, abs=10)
    assert beam.getInternalMomentumStrength(1500-e) == approx(0, abs=10)
    
    
def get_ftool_fconcrete_comparisson(beam, file_shear, file_momentum):
    
    x_shear, shear_diagram_v47 = np.loadtxt(file_shear).T
    x_shear = x_shear*100
    not_duplicated_x = ~duplicated(x_shear)
    x_shear = x_shear[not_duplicated_x][1:-1]
    shear_diagram_v47 = shear_diagram_v47[not_duplicated_x][1:-1]
    shear_fconcrete = beam.getInternalShearStrength(x_shear)


    x_momentum, momentum_diagram_v47 = np.loadtxt(file_momentum).T
    x_momentum = 100*x_momentum
    not_duplicated_x = ~duplicated(x_momentum)
    x_momentum = x_momentum[not_duplicated_x][1:-1]
    momentum_diagram_v47 = momentum_diagram_v47[not_duplicated_x][1:-1]*100
    momentum_fconcrete = beam.getInternalMomentumStrength(x_momentum)

    
    return (shear_diagram_v47, shear_fconcrete) , (momentum_diagram_v47, momentum_fconcrete)
    
def beam47_creation():
    
    material = Material(E=3*10**7, poisson=1, alpha=1)
    section = Rectangle(25,44.6, material)

    f1 = Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
    f2 = Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
    f3 = Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=113)
    n3 = Node.SimpleSupport(x=583)
    n4 = Node.SimpleSupport(x=1188)

    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    bar3 = SingleBeamElement([n3, n4], section)

    beam = Beam(
        loads = [f1, f2, f3],
        bars = [bar1, bar2, bar3]
    )
    return beam

def test_beam47():
    assert beam47_creation()
    
def test_shear_diagram_beam47():
    beam = beam47_creation()
    shear_info, momentum_info = get_ftool_fconcrete_comparisson(beam,
                                    r"tests/structural/shear_diagram_v47.txt",
                                    r"tests/structural/momentum_diagram_v47.txt")
    
    shear_diagram_v47, shear_fconcrete = shear_info
    momentum_diagram_v47, momentum_fconcrete = momentum_info
    
    assert shear_fconcrete == approx(shear_diagram_v47, abs=1)
    assert momentum_fconcrete == approx(momentum_diagram_v47, abs=100)
    