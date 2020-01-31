from fconcrete import config, duplicated, Material, Beam, Load, Node, ConcreteBeam, BeamElement, Rectangle, Concrete, Section
e = config.e
from pytest import approx
import numpy as np
import os

def approx01(x):
    return approx(x, abs=0.1)

def create_crimped_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-1, x=500)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=1000)
    bar1 = BeamElement([n1, n2], section, material)
    return Beam(
        loads = [f1],
        beam_elements = [bar1],
        solve_structural=False
    )
    
def create_simple_beam():
    material = Material(E=1, poisson=0.3, alpha=1)
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-1, x=500)
    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=1000)
    bar1 = BeamElement([n1, n2], section, material)
    return Beam(
        loads = [f1],
        beam_elements = [bar1],
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
    support_reaction = beam.nodal_efforts
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
    support_reaction = beam.nodal_efforts
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
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-200, x=200)
    n1 = Node.Crimp(x=0)
    n2 = Node.Crimp(x=1000)
    bar1 = BeamElement([n1, n2], section, material)
    beam = Beam(
        loads = [f1],
        beam_elements = [bar1]
    )
    support_reaction = beam.nodal_efforts
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
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    bar1 = BeamElement([n1, n2], section, material)
    beam = Beam(
        loads = [f1],
        beam_elements = [bar1]
    )
    support_reaction = beam.nodal_efforts
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
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    n3 = Node.Crimp(x=1500)
    bar1 = BeamElement([n1, n2], section, material)
    bar2 = BeamElement([n2, n3], section, material)
    beam = Beam(
        loads = [f1],
        beam_elements = [bar1, bar2],
    )
    support_reaction = beam.nodal_efforts
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
    section = Rectangle(12,1)
    f1 = Load.PontualLoad(-200, x=700)
    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=1000)
    n3 = Node.SimpleSupport(x=1500)
    bar1 = BeamElement([n1, n2], section, material)
    bar2 = BeamElement([n2, n3], section, material)
    beam = Beam(
        loads = [f1],
        beam_elements = [bar1, bar2],
    )
    support_reaction = beam.nodal_efforts
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