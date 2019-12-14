from fconcrete import e, Material, Beam, Load, Node, ConcreteBeam, SingleBeamElement, Rectangle, Concrete, Section, ConcreteSteels
from pytest import approx

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
    assert beam.getInternalMomentumStrength(e) == approx(1*10/8, abs=0.001)
    assert beam.getInternalMomentumStrength(beam.length-e) == approx(1*10/8, abs=0.001)
    assert beam.getInternalMomentumStrength(beam.length/2) == approx(1*10/8+0.5*5, abs=0.001)
    


def a_test_structural_matrix_rigity_global():
    beam.matrix_rigidity_global() == np.array([])