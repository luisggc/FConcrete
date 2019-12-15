from fconcrete import e, Material, Beam, Load, Node, ConcreteBeam, SingleBeamElement, Rectangle, Concrete, Section, ConcreteSteels
from pytest import approx
import numpy as np
import os

def approx01(x):
    return approx(x, abs=0.1)

def create_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-1, x=5)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=10)
    bar1 = SingleBeamElement([n1, n2], section)
    return Beam(
        loads = [f1],
        bars = [bar1]
    )
    
def create_simple_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-1, x=5)
    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=10)
    bar1 = SingleBeamElement([n1, n2], section)
    return Beam(
        loads = [f1],
        bars = [bar1]
    )
    
def test_structural_create_simple_beam():
    beam = create_simple_beam()
    assert beam.solve() == None
    

def test_structural_create_crimped_beam():
    beam = create_crimped_beam()
    assert beam.solve() == None

def test_structural_simple_beam():
    beam = create_simple_beam()
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(0.5)
    assert support_reaction[1] == approx(0)
    assert support_reaction[-2] == approx(0.5)
    assert support_reaction[-1] == approx(0)
    assert beam.getInternalMomentumStrength(beam.length/2) == approx(1*10/4)
    assert beam.getInternalShearStrength(beam.length/2-e) == approx(0.5)
    assert beam.getInternalShearStrength(beam.length/2+e) == approx(-0.5)
    
def test_structural_crimped_beam():
    beam = create_crimped_beam()
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(0.5)
    assert support_reaction[1] == approx(1*10/8)
    assert support_reaction[-2] == approx(0.5)
    assert support_reaction[-1] == approx(-1*10/8)
    assert beam.getInternalShearStrength(beam.length/2-e) == approx(0.5)
    assert beam.getInternalShearStrength(beam.length/2+e) == approx(-0.5)
    assert beam.getInternalMomentumStrength(e) == approx(-1*10/8, abs=0.001)
    assert beam.getInternalMomentumStrength(beam.length-e) == approx(-1*10/8, abs=0.001)
    assert beam.getInternalMomentumStrength(beam.length/2) == approx(-1*10/8+0.5*5, abs=0.001)
    
def test_structural_double_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=2)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=10)
    bar1 = SingleBeamElement([n1, n2], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1]
    )
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(179.2, abs=0.1)
    assert support_reaction[1] == approx(256, abs=0.1)
    assert support_reaction[-2] == approx(20.8, abs=0.1)
    assert support_reaction[-1] == approx(-64, abs=0.1)
    assert beam.getInternalShearStrength(1.5) == approx(179.2, abs=0.1)
    assert beam.getInternalShearStrength(3) == approx(-20.8, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-256, abs=0.1)
    assert beam.getInternalMomentumStrength(2) == approx(+102.4, abs=0.1)
    assert beam.getInternalMomentumStrength(1.7) == approx(48.6, abs=0.1)
    assert beam.getInternalMomentumStrength(2.1) == approx(100.3, abs=0.1)
    assert beam.getInternalMomentumStrength(10-e) == approx(-64, abs=0.1)
    
def test_structural__crimped_simple_supported_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=7)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=10)
    bar1 = SingleBeamElement([n1, n2], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1]
    )
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(87.3, abs=0.1)
    assert support_reaction[1] == approx(273, abs=0.1)
    assert support_reaction[-2] == approx(112.7, abs=0.1)
    assert support_reaction[-1] == approx(0, abs=0.1)
    assert beam.getInternalShearStrength(1) == approx(87.3, abs=0.1)
    assert beam.getInternalShearStrength(8) == approx(-112.7, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-273, abs=0.1)
    assert beam.getInternalMomentumStrength(1) == approx(-185.7, abs=0.1)
    assert beam.getInternalMomentumStrength(8) == approx(+225.4, abs=0.1)
    assert beam.getInternalMomentumStrength(10-e) == approx(0, abs=0.1)
    
def test_structural__crimped_simplesupported_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=7)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=10)
    n3 = Node.Crimp(x=15)
    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1, bar2]
    )
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(57.9, abs=0.1)
    assert support_reaction[1] == approx(175, abs=0.1)
    assert support_reaction[-4] == approx(200.9, abs=0.1)
    assert support_reaction[-3] == approx(0, abs=0.1)
    assert support_reaction[-2] == approx(-58.8, abs=0.1)
    assert support_reaction[-1] == approx(98, abs=0.1)
    
    assert beam.getInternalShearStrength(1) == approx(57.9, abs=0.1)
    assert beam.getInternalShearStrength(8) == approx(-142.1, abs=0.1)
    assert beam.getInternalShearStrength(12) == approx(58.8, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-175, abs=0.1)
    assert beam.getInternalMomentumStrength(1) == approx(-117.1, abs=0.1)
    assert beam.getInternalMomentumStrength(8) == approx(88.2, abs=0.1)
    assert beam.getInternalMomentumStrength(12) == approx(-78.4, abs=0.1)
    assert beam.getInternalMomentumStrength(15-e) == approx(98, abs=0.1)
    
def test_structural__crimped_simplesupported_simplesupported_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1, material)
    f1 = Load.PontualLoad(-200, x=7)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=10)
    n3 = Node.SimpleSupport(x=15)
    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    beam = Beam(
        loads = [f1],
        bars = [bar1, bar2]
    )
    beam.solve()
    support_reaction = beam.getSupportReactions()
    assert support_reaction[0] == approx(60.8, abs=0.1)
    assert support_reaction[1] == approx(184.8, abs=0.1)
    assert support_reaction[-4] == approx(174.4, abs=0.1)
    assert support_reaction[-3] == approx(0, abs=0.1)
    assert support_reaction[-2] == approx(-35.3, abs=0.1)
    assert support_reaction[-1] == approx(0, abs=0.1)
    
    assert beam.getInternalShearStrength(1) == approx(60.8, abs=0.1)
    assert beam.getInternalShearStrength(8) == approx(-139.2, abs=0.1)
    assert beam.getInternalShearStrength(12) == approx(35.3, abs=0.1)
    assert beam.getInternalMomentumStrength(e) == approx(-184.8, abs=0.1)
    assert beam.getInternalMomentumStrength(1) == approx(-124, abs=0.1)
    assert beam.getInternalMomentumStrength(8) == approx(101.9, abs=0.1)
    assert beam.getInternalMomentumStrength(12) == approx(-105.8, abs=0.1)
    assert beam.getInternalMomentumStrength(15-e) == approx(0, abs=0.1)
    
    
    
    

def test_beam47():

    material = Material(E=3*10**7, poisson=1, alpha=1)
    section = Rectangle(0.25,0.446, material)

    f1 = Load.UniformDistributedLoad(-16.22, x_begin=0, x_end=1.13)
    f2 = Load.UniformDistributedLoad(-49.94, x_begin=1.13, x_end=5.83)
    f3 = Load.UniformDistributedLoad(-41.96, x_begin=5.83, x_end=11.88)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=1.13)
    n3 = Node.SimpleSupport(x=5.83)
    n4 = Node.SimpleSupport(x=11.88)

    bar1 = SingleBeamElement([n1, n2], section)
    bar2 = SingleBeamElement([n2, n3], section)
    bar3 = SingleBeamElement([n3, n4], section)

    beam = Beam(
        loads = [f1, f2, f3],
        bars = [bar1, bar2, bar3]
    )
    beam.solve()
    
    x_ftool, shear_diagram_v47 = np.loadtxt(r"tests/structural/shear_diagram_v47.txt").T
    shear_fconcrete = beam.getInternalShearStrength(x_ftool)
    
    assert shear_diagram_v47 == approx01(shear_fconcrete)
    