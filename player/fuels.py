from enum import auto, Enum

class FuelTypes(Enum):
    Hedrol=auto()
    Nuclent=auto()
    Plasvo=auto()

class Fuel:
    def __init__(self, name:str, _type:str, amount:float, efficiency:float) -> None:
        self.name = name
        self.type = _type
        self.amount = amount
        self.efficiency = efficiency

class Hedrol(Fuel):
    def __init__(self, amount: float) -> None:
        super().__init__("Hedrol", FuelTypes.Hedrol, amount, 1)

class Nuclent(Fuel):
    def __init__(self, amount: float) -> None:
        super().__init__("Nuclent", FuelTypes.Nuclent, amount, 1.2)

class Plasvo(Fuel):
    def __init__(self, amount: float) -> None:
        super().__init__("Plasvo", FuelTypes.Plasvo, amount, 1.6)
