Analysis Usage Example
==========================


First of all we have to create a function that we input the parameters that we want to make the analysis and return a concrete_beam.

More information about the ConcreteBeam class :doc:`click here <../fconcrete.StructuralConcrete.ConcreteBeam>`.

Let's see an example:

.. ipython:: python
                                                      
    def concrete_beam_function(width, height):
           n1 = fc.Node.SimpleSupport(x=0)
           n2 = fc.Node.SimpleSupport(x=200)
           pp = fc.Load.UniformDistributedLoad(-width*height*25/1000000, x_begin=0, x_end=200)
           f1 = fc.Load.UniformDistributedLoad(-0.01, x_begin=0, x_end=1)
           beam = fc.ConcreteBeam(
               loads = [f1, pp],
               nodes = [n1, n2],
               section = fc.Rectangle(height,width),
               division = 200
           )
           return beam

Now we can use the Analysis class to loop through the possibilities.
In this example, we are going to set **avoid_estimate=True** and **show_progress=False** because it is a statical demonstration, but It is good practice to keep the default values.

The first argument is always the **function** that you created before, then you can set or disable some **optinal features** and finally you **must** 
provide values for the same inputs that are necessary on the concrete_beam_function **with the same name**.
In this case, we have choosen width and height to change, so we can provide a list os possible values. See the example:


.. ipython:: python

    import fconcrete as fc
    full_report, solution_report, best_solution = fc.Analysis.getBestSolution(
                                        concrete_beam_function,
                                        max_steps_without_decrease=15,
                                        sort_by_multiplication=True,
                                        avoid_estimate=True,
                                        show_progress=False,
                                        width=[15, 17, 19],
                                        height=[30, 34, 38])

Instead of providing a list such as width=[15, 17, 19], you can also provide a tuple like that: **(start, end_but_not_included, steps)**.
It is going to create a list for you. Both ways have the same effect::

    width = (15, 31, 2)
    width = [15, 17, 19, 21, 23, 25, 27, 29]

Once the reports are created, we can see its information:

.. ipython:: python

    full_report

    # We can see that the error column just have empty strings, so in this case no errors of combinations were found.
    # The solution (only without the errors) table is sorted by cost ascending, so the first one is the most economic solution.


A alternative way to see the beast beam and its properties:

.. ipython:: python

    best_solution

The first values are the parameters to be analysed and the last columns are
'cost' (total cost) and the cost for the 3 elements: 'Concrete', 'Longitudinal bar' and 'Transversal bar'.