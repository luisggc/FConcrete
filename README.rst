=========
FConcrete
=========


.. image:: https://img.shields.io/pypi/v/fconcrete.svg
        :target: https://pypi.python.org/pypi/fconcrete

.. image:: https://img.shields.io/travis/luisggc/fconcrete.svg
        :target: https://travis-ci.org/luisggc/fconcrete

.. image:: https://readthedocs.org/projects/fconcrete/badge/?version=latest
        :target: https://fconcrete.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Concrete beams according to NBR:6118:2014.
Usage examples `here`_.

* Free software: MIT license
* Documentation: https://fconcrete.readthedocs.io.

Warning: This is a project in a alpha version. Much testing is needed yet. **Do not use on your real life projects.**

A Quick Introduction
--------------------

FConcrete is a python package to calculate the steel bars (longitudinal and transversal) with less material cost as possible and in a human friendy way (see default configs)::

        n1 = fc.Node.SimpleSupport(x=0)
        n2 = fc.Node.SimpleSupport(x=400)
        f1 = fc.Load.UniformDistributedLoad(-0.3, x_begin=0, x_end=400)

        concrete_beam = fc.ConcreteBeam(
                loads = [f1],
                nodes = [n1, n2],
                section = fc.Rectangle(30,80),
                division = 200
        )

It is also implemented a `Analysis Class`_ that can help you to get the best retangular section for your beam.
As you can see on the documentations, by the default all units are in cm, kN or combination of both.

Features
--------

- Export plots to dxf
- Define input parameters: available materials, cost, geometry definition, loads, fck, etc
- Calculation of efforts at any point
- Moment diagram decalaged
- Section balance and calculation of the required steel area
- Anchorage length
- Remove longitudinal bars
- Calculation of transversal steel bar (area per cm)
- Check limits and spacing per transversal bar span
- Check compliance with the steel area limits
- Calculation of rotation at any point
- Calculation of displacement at any point
- Implement test routines comparing Ftool
- Check dimensioning in E.L.S (except rupture)
- Associate costs with materials
- Program expense calculation function
- Create interaction functions and create table to follow the convergence of the algorithm
- Examples of tool usage (completion for optimized pre-dimensioning)
- Program expense calculation function
- Documentation
- Dinamic calculation of d (steel height) when there is change of the expected steel position
- API to easy connection

TODO
----

- Check rupture (ELS)
- Check minimum area on the support
- Correct displacement value when there is variation of E * I along the beam
- Plot correctly when stirrups are not vertical
- Plot longitudinal bars correctly when the height or position of the beam base changes.
- Calculate the total length of the bar correctly when the height or position of the beam base changes.
- Implement compression armor


Installation
------------

To install FConcrete, run this command in your terminal:

.. code-block:: console

    $ pip install fconcrete

This is the preferred method to install FConcrete, as it will always install the most recent stable release.
If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/



Credits
-------

Most of vectorized calculus made with Numpy_, unit conversion with Pint_, all plots with Matplotlib_ (export to dxf with ezdxf_), detect peaks with py-findpeaks_, 
docs made with the help of Sphinx_ and Numpydoc_, analysis table with Pandas_,  
this package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Pint: https://github.com/hgrecco/pint
.. _Numpydoc: https://github.com/numpy/numpydoc
.. _Numpy: https://github.com/numpy/numpy
.. _Matplotlib: https://github.com/matplotlib/matplotlib
.. _py-findpeaks: https://github.com/MonsieurV/py-findpeaks
.. _Sphinx: https://github.com/sphinx-doc/sphinx
.. _Pandas: https://github.com/pandas-dev/pandas
.. _ezdxf: https://github.com/mozman/ezdxf
.. _`here`: https://fconcrete.readthedocs.io/en/latest/usage.html
.. _`Analysis Class`: https://fconcrete.readthedocs.io/en/latest/fconcrete.StructuralConcrete.Analysis.html
