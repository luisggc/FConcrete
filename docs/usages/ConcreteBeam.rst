ConcreteBeam Usage Example
==========================


How to create a beam:

.. ipython:: python

    import fconcrete as fc

    n1 = fc.Node.SimpleSupport(x=0, length=20)
    n2 = fc.Node.SimpleSupport(x=400, length=20)
    f1 = fc.Load.UniformDistributedLoad(-0.6, x_begin=0, x_end=400)

    concrete_beam = fc.ConcreteBeam(
        loads = [f1],
        nodes = [n1, n2],
        section = fc.Rectangle(30,80),
        division = 200
    )

You can use all properties and methods of the :doc:`ConcreteBeam Class <../fconcrete.StructuralConcrete.ConcreteBeam>` including :doc:`Beam Class <../fconcrete.Structural.Beam>` such as plot shear diagram, momentum, etc.
See examples in :doc:`Beam usage example <./Beam>`.

See general information:

.. ipython:: python

    print("Cost of the concrete beam, in reais: ", concrete_beam.cost)
    print("Processing time of the concrete beam, in seconds: ", concrete_beam.processing_time)
    print(concrete_beam.cost_table)

Plot longitudinal informations:

.. ipython:: python

    # Longitudinal steel
    @savefig long_steel_bars.png
    concrete_beam.long_steel_bars.plot(prop='area_accumulated')

.. ipython:: python

    # Transversal steel
    @savefig transv_steel_bars_plotLong.png
    concrete_beam.transv_steel_bars.plotLong()

Plot transversal section:

.. ipython:: python

    @savefig plotTransversalInX.png
    concrete_beam.plotTransversalInX(200)
