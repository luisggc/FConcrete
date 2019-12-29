from pint import UnitRegistry
ureg = UnitRegistry()
ureg.define('kn_cm2 = kilonewton / centimeter ** 2 = kn_cm2')
ureg.define('kNcm = kilonewton * centimeter = kncm')
ureg.define('kNm = kilonewton * meter = knm')
_Q = ureg.Quantity

e = 0.00001

from fconcrete.AvailableMaterials import AvailableConcreteSteelBar

available_material = {
    "concrete_steel_bars": AvailableConcreteSteelBar(),
    "steel_bar_surface_type": "ribbed"
}