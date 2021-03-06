from fconcrete import config, duplicated, Material, Beam, Load, Node, ConcreteBeam, BeamElement, Rectangle, Concrete, Section
e = config.e
from pytest import approx
import numpy as np
import os

def approx01(x):
    return approx(x, abs=0.1)


def compare(beam, name, ftool_displacement_in_mm=False):
    shear_info, momentum_info, displacement_info, rotation_info = get_ftool_fconcrete_comparisson(beam,
                                    r"tests/structural/{}/shear.txt".format(name),
                                    r"tests/structural/{}/momentum.txt".format(name),
                                    r"tests/structural/{}/displacement.txt".format(name))
    
    shear_diagram_ftool, shear_fconcrete = shear_info
    momentum_diagram_ftool, momentum_fconcrete = momentum_info
    rotation_diagram_ftool, rotation_fconcrete = rotation_info
    displacement_diagram_ftool, displacement_fconcrete = displacement_info
    displacement_diagram_ftool = displacement_diagram_ftool/10 if ftool_displacement_in_mm else displacement_diagram_ftool
    
    assert shear_diagram_ftool == approx(shear_fconcrete, abs=0.00001)
    assert momentum_diagram_ftool == approx(momentum_fconcrete, abs=0.001)
    assert rotation_diagram_ftool == approx(rotation_fconcrete, abs=0.000001)
    assert displacement_diagram_ftool == approx(displacement_fconcrete, abs=0.000001)

def get_ftool_fconcrete_comparisson(beam, file_shear, file_momentum, file_displacement):
    
    x_shear, shear_diagram_v47 = np.loadtxt(file_shear).T             
    not_duplicated_x = ~duplicated(x_shear)
    x_shear = x_shear[not_duplicated_x][1:-1]
    shear_diagram_v47 = shear_diagram_v47[not_duplicated_x][1:-1]
    shear_fconcrete = beam.getInternalShearStrength(x_shear)


    x_momentum, momentum_diagram_v47 = np.loadtxt(file_momentum).T
    not_duplicated_x = ~duplicated(x_momentum)
    x_momentum = x_momentum[not_duplicated_x][1:-1]
    momentum_diagram_v47 = momentum_diagram_v47[not_duplicated_x][1:-1]
    momentum_fconcrete = beam.getInternalMomentumStrength(x_momentum)

    x_ftool, _, displacement_diagram_v47, rotation_diagram_v47 = np.loadtxt(file_displacement).T
    not_duplicated_x = ~duplicated(x_ftool)

    not_duplicated_x_displacement = not_duplicated_x & ~(displacement_diagram_v47 == 0)
    x_displacement = x_ftool[not_duplicated_x_displacement]
    displacement_diagram_v47 = displacement_diagram_v47[not_duplicated_x_displacement]
    displacement_fconcrete = beam.getDisplacement(x_displacement)

    x_rotation = x_ftool[not_duplicated_x]
    rotation_diagram_v47 = rotation_diagram_v47[not_duplicated_x]
    rotation_fconcrete = beam.getRotation(x_rotation)

    return (shear_diagram_v47, shear_fconcrete), (momentum_diagram_v47, momentum_fconcrete), (displacement_diagram_v47, displacement_fconcrete), (rotation_diagram_v47, rotation_fconcrete) 
    

def test_v47():
    material = Material(E='27000 MPa', poisson=1, alpha=1)
    section = Rectangle(25,44.6)

    f1 = Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
    f2 = Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
    f3 = Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=113)
    n3 = Node.SimpleSupport(x=583)
    n4 = Node.SimpleSupport(x=1188)

    bar1 = BeamElement([n1, n2], section, material)
    bar2 = BeamElement([n2, n3], section, material)
    bar3 = BeamElement([n3, n4], section, material)

    beam = Beam(
        loads = [f1, f2, f3],
        beam_elements = [bar1, bar2, bar3]
    )
    compare(beam=beam, name="v47", ftool_displacement_in_mm=True)
    

def test_free_crimped():
    material = Material(E='27000 MPa', poisson=1, alpha=1)
    section = Rectangle(25,44.6)

    f1 = Load.PontualLoad(-5, x=29)
    f2 = Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)

    n1 = Node.Free(x=0)
    n2 = Node.Crimp(x=113)

    bar1 = BeamElement([n1, n2], section, material)

    beam = Beam(
        loads = [f1, f2],
        beam_elements = [bar1]
    )
    compare(beam=beam, name="free_crimped", ftool_displacement_in_mm=True)

def test_crimped_free():
    material = Material(E='27000 MPa', poisson=1, alpha=1)
    section = Rectangle(25,44.6)

    f1 = Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)

    n1 = Node.Crimp(x=0)
    n2 = Node.Free(x=113)

    bar1 = BeamElement([n1, n2], section, material)

    beam = Beam(
        loads = [f1],
        beam_elements = [bar1]
    )
    compare(beam=beam, name="crimped_free", ftool_displacement_in_mm=True)
    
    
def test_crimped_simple_supported():
    material = Material(E='27000 MPa', poisson=1, alpha=1)
    section = Rectangle(25,44.6)

    f1 = Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)

    n1 = Node.Crimp(x=0)
    n2 = Node.SimpleSupport(x=113)

    bar1 = BeamElement([n1, n2], section, material)

    beam = Beam(
        loads = [f1],
        beam_elements = [bar1]
    )
    compare(beam=beam, name="crimped_simple_supported", ftool_displacement_in_mm=True)
    
def test_simple_simple_simple():
    base, altura, comprimento = 57, 107, 1100
    pp = Load.UniformDistributedLoad(-0.1375, x_begin=0, x_end=comprimento)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=comprimento/2)
    n3 = Node.SimpleSupport(x=comprimento)

    be1 = BeamElement([n1, n2], Rectangle(base, altura), Material(10000,1,1))
    be2 = BeamElement([n2, n3], Rectangle(base, altura), Material(10000,1,1))

    beam = Beam(loads=[pp], beam_elements=[be1, be2])
    compare(beam=beam, name="simple_simple_simple")
    

def test_simple_simple_simple_partial_load():
    base, altura, comprimento = 57, 107, 1100
    pp = Load.UniformDistributedLoad(-0.1375, x_begin=250, x_end=600)

    n1 = Node.SimpleSupport(x=0)
    n2 = Node.SimpleSupport(x=comprimento/2)
    n3 = Node.SimpleSupport(x=comprimento)

    be1 = BeamElement([n1, n2], Rectangle(base, altura), Material(10000,1,1))
    be2 = BeamElement([n2, n3], Rectangle(base, altura), Material(10000,1,1))

    beam = Beam(loads=[pp], beam_elements=[be1, be2])
    compare(beam=beam, name="simple_simple_simple_partial_load")


#for x, ft, fc in zip(x_momentum, momentum_diagram_ftool, momentum_fconcrete):
#    if ft != approx(fc, abs=0.000001):
#        print(x, ft, fc)