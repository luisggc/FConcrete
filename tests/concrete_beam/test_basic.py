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
    section = fc.Rectangle(25,56, material)

    #Design
    f1 = fc.Load.UniformDistributedLoad(-0.1622, x_begin=0, x_end=113)
    f2 = fc.Load.UniformDistributedLoad(-0.4994, x_begin=113, x_end=583)
    f3 = fc.Load.UniformDistributedLoad(-0.4196, x_begin=583, x_end=1188)

    n1 = fc.Node.SimpleSupport(x=0, length=20)
    n2 = fc.Node.SimpleSupport(x=113, length=20)
    n3 = fc.Node.SimpleSupport(x=583, length=20)
    n4 = fc.Node.SimpleSupport(x=1188, length=20)

    bar1 = fc.SingleBeamElement([n1, n2], section)
    bar2 = fc.SingleBeamElement([n2, n3], section)
    bar3 = fc.SingleBeamElement([n3, n4], section)

    fc.config.available_material = {
        "concrete_long_steel_bars":fc.AvailableLongConcreteSteelBar(diameters=[8]),
        "concrete_transv_steel_bars":fc.AvailableTransvConcreteSteelBar(diameters=[8]),
    }
        
    beam = fc.ConcreteBeam(
        loads = [f1, f2, f3],
        beam_elements = [bar1, bar2, bar3],
        bar_steel_max_removal = 2,
    )
    return beam
    
def test_create_concrete_beam():
    beam = create_concrete_beam()
    assert beam.solve_structural() == None
    