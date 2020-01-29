=====
Usage
=====

To use FConcrete in a project::

    import fconcrete as fc

Now you can use the project.

    import fconcrete as fc
    
    n1 = fc.Node.SimpleSupport(x=0)
    n2 = fc.Node.SimpleSupport(x=250)
    n3 = fc.Node.SimpleSupport(x=500)

    f1 = fc.Load.UniformDistributedLoad(-0.1, x_begin=0, x_end=250)
    f2 = fc.Load.UniformDistributedLoad(-0.3, x_begin=250, x_end=500)

    section = fc.Rectangle(12, 25)
    material = fc.Material(E=10**6, poisson=1, alpha=1)

    beam_element_1 = fc.BeamElement([n1, n2], section, material)
    beam_element_2 = fc.BeamElement([n2, n3], section, material)

    beam = fc.Beam(loads=[f1, f2], beam_elements=[beam_element_1, beam_element_2])
    beam.plotShearDiagram()