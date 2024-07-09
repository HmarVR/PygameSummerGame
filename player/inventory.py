from tools import ToolTypes, AlumitePickaxe
from fuels import Hedrol


class Inventory:
    def __init__(self, fuel = None, resources = [], tools = None) -> None:
        self.fuel = fuel
        self.resources = resources
        self.tools = self.init_tools() if tools == None else tools

    @staticmethod
    def init_fuel():
        return Hedrol()
    
    @staticmethod
    def init_resources():
        return []
    
    @staticmethod
    def init_tools():
        return {ToolTypes.pickaxe : AlumitePickaxe()}
