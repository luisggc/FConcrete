from pytest import approx
import numpy as np
import os
import fconcrete as fc
import matplotlib.pyplot as plt
np.set_printoptions(precision=3, suppress=True, linewidth=3000)

def approx01(x):
    return approx(x, abs=0.1)

def create_concrete_beam():
    material = fc.Concrete(fck='30 MPa', aggressiveness=2)
    section = fc.Rectangle(25,60)

    #Design
    f1 = fc.Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
    f2 = fc.Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
    f3 = fc.Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

    n1 = fc.Node.SimpleSupport(x=0, length=20)
    n2 = fc.Node.SimpleSupport(x=113, length=20)
    n3 = fc.Node.SimpleSupport(x=583, length=20)
    n4 = fc.Node.SimpleSupport(x=1188, length=20)

    bar1 = fc.BeamElement([n1, n2], section, material)
    bar2 = fc.BeamElement([n2, n3], section, material)
    bar3 = fc.BeamElement([n3, n4], section, material)
        
    beam = fc.ConcreteBeam(
        loads = [f1, f2, f3],
        beam_elements = [bar1, bar2, bar3],
        bar_steel_max_removal = 2,
        consider_own_weight = False
    )
    return beam
    
def test_create_concrete_beam():
    beam = create_concrete_beam()
    assert beam.processing_time>0
    