
from fconcrete import Load, Node, Beam, SingleBeamElement, Concrete, Rectangle, Section, ConcreteSteels

material = Concrete(fck=30, aggressiveness=3)
section = Rectangle(1000,100000, material)

f1 = Load.PontualLoad(-20000, x=2)
f4 = Load.UniformDistributedLoad(-100000000, x_begin=0, x_end=4)

n1 = Node.SimpleSupport(x=0)
n2 = Node.SimpleSupport(x=4)
n3 = Node.SimpleSupport(x=6)

bar1 = SingleBeamElement([n1, n2], section)
bar2 = SingleBeamElement([n2, n3], section)

beam = Beam(
    loads = [f4],
    bars = [bar1, bar2],
    steel= ConcreteSteels(diameters=[8])
)



