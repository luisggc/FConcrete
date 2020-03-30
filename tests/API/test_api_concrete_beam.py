from pytest import approx
import fconcrete as fc

def test_api_concrete_beam():
    income = '''
    {
        "ConcreteBeam": {
            "section": {
                "width": 30,
                "height": 80,
                "type": "Rectangle"
            },
            "nodes": [
                {
                    "x": 0,
                    "length": 20,
                    "type": "SimpleSupport"
                },
                {
                    "x": 400,
                    "length": 40,
                    "type": "SimpleSupport"
                }
            ],
            "loads": [
                {
                    "q": -0.3,
                    "x_begin": 0,
                    "x_end": 400,
                    "type": "UniformDistributedLoad"
                },
                {
                    "load": -0.5,
                    "x": 150,
                    "type": "PontualLoad"
                }
            ],
            "design_factor": 1.4
        }
    }
    '''

    parsed = fc.API(income)
    parsed_concrete_beam = parsed.concrete_beam

    n1 = fc.Node.SimpleSupport(x=0, length=20)
    n2 = fc.Node.SimpleSupport(x=400, length=40)
    f1 = fc.Load.UniformDistributedLoad(-0.3, x_begin=0, x_end=400)
    f2 = fc.Load.PontualLoad(-0.5, x=150)

    concrete_beam2 = fc.ConcreteBeam(
            loads = [f1, f2],
            nodes = [n1, n2],
            section = fc.Rectangle(30,80),
    )

    concrete_beam2.cost

    assert parsed_concrete_beam.cost == concrete_beam2.cost