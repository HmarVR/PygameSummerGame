from enum import auto, Enum

class ToolTypes:
    pickaxe = auto()

class Tier:
    def __init__(self, speed:float, tier:int) -> None:
        self.speed = speed
        self.tier = tier

class Tool:
    def __init__(self, name:str, _type:ToolTypes, tier:int) -> None:
        self.name = name
        self.type = _type
        self.tier = tier

class Pickaxe(Tool):
    def __init__(self, name:str, tier: Tier) -> None:
        super().__init__(name, ToolTypes.pickaxe, tier)

class AlumitePickaxe(Pickaxe):
    def __init__(self) -> None:
        super().__init__("Alumite Pickaxe", Tier(1, 0))

class AuramitePickaxe(Pickaxe):
    def __init__(self) -> None:
        super().__init__("Auramite Pickaxe", Tier(1.2, 1))

class AetheriumPickaxe(Pickaxe):
    def __init__(self) -> None:
        super().__init__("Aetherium Pickaxe", Tier(1.5, 2))

class AzuriumPickaxe(Pickaxe):
    def __init__(self) -> None:
        super().__init__("Azurium Pickaxe", Tier(2, 3))
