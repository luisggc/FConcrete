Beam Usage Example
==================

How to create a beam:

.. ipython:: python

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

You can use all properties and methods of the :doc:`Beam Class <../fconcrete.Structural.Beam>` such as plot shear diagram, momentum, etc.

Plot Shear Diagram:

.. ipython:: python

    @savefig plotShearDiagram.png
    beam.plotShearDiagram()

Plot Momentum Diagram:

.. ipython:: python

    @savefig plotMomentumDiagram.png
    beam.plotMomentumDiagram()

Plot Displacement Diagram:

.. ipython:: python

    @savefig plotDisplacementDiagram.png
    beam.plotDisplacementDiagram()

If you only want to get the values, but not to plot. You can use the "get" instead of "plot".

.. ipython:: python

    x, displacement = beam.getDisplacementDiagram()
    print(x[0:10])
    print(displacement[0:10])


Plot of the beam:

.. ipython:: python

    @savefig plotBeam.png
    beam.plot()