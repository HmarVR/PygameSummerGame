import src.background as background
import src.event_manager as event_manager
import src.sun as sun
import src.tilemap as tilemap
import src.main_menu as main_menu
import src.planet as planet
import src.planet_manager as planet_manager
import src.postprocessor as postprocessor
import src.player as player

from src.space_menu import SpaceMenu
from src.spaceship import SpaceShip

MainMenu = main_menu.MainMenu
PlanetManager = planet_manager.PlanetManager
Planet = planet.Planet

Background = background.Background
ProcessRender = postprocessor.ProcessRender
EventManager = event_manager.EventManager

Sun = sun.Sun
Tilemap = tilemap.Tilemap
Player = player.Player

SpaceMenu = SpaceMenu
SpaceShip = SpaceShip