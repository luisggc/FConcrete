=====
Usage
=====

To use FConcrete in a project::

    import fconcrete as fc


How to create a beam:

.. literalinclude:: usages/Beam/createBeamExample.py
  :language: py


You can use all properties and methods of the Beam class such as plot shear diagram, momentum, etc.

Plot Shear Diagram::

    beam.plotShearDiagram()

.. plot:: usages/Beam/plotShearDiagram.py

Plot Momentum Diagram::

    beam.plotMomentumDiagram()

.. plot:: usages/Beam/plotMomentumDiagram.py

Plot Displacement Diagram::

    beam.plotDisplacementDiagram()

.. plot:: usages/Beam/plotDisplacementDiagram.py

If you only want to get the values, but not to plot. You can use the "get" instead of "plot".

.. ipython:: python

    import fconcrete as fc
    print("olaaaaa")
    a=5
    print(a)

Texto blabal

 .. ipython:: python

    print(a)