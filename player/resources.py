from enum import auto, Enum

class ResourceTypes(Enum):
    Alumite=auto()
    Auramite=auto()
    Aetherium=auto()
    Azurium=auto()


class Resource:
    def __init__(self, name:str, _type:str, amount:float) -> None:
        self.name = name
        self.type = _type
        self.amount = amount

class Alumite(Resource):
    def __init__(self, amount: float) -> None:
        super().__init__("Alumite", ResourceTypes.Alumite, amount)

class Auramite(Resource):
    def __init__(self, amount: float) -> None:
        super().__init__("Auramite", ResourceTypes.Auramite, amount)

class Aetherium(Resource):
    def __init__(self, amount: float) -> None:
        super().__init__("Aetherium", ResourceTypes.Aetherium, amount)

class Azurium(Resource):
    def __init__(self, amount: float) -> None:
        super().__init__("Azurium", ResourceTypes.Azurium, amount)

