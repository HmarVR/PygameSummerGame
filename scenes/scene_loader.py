from scenes.planet_scene import PlanetScene
from scenes.menu_scene import MenuScene
from scenes.space_scene import SpaceScene

menu = MenuScene
space = SpaceScene
planet = PlanetScene

GAMESCENES = {
    'menu': menu,
    'space': space,
    'planet': planet,
}

default_scene = 'menu'