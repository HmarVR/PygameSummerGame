import pygame as pg
import zengl, glm
import zengl_extras
import sys, time

from camera import Camera
from mesh import Mesh
from model import *
from scene import Scene
from vao import *
from vbo import *
from fbo import *
from shader_program import *
from texture import *

class PC_Game:
    def __init__(self, win_size=(682, 362)):
        # init pygame modules
        pg.init()
        
        # why u dont try to use GPU, (Or you cant do that)
        try:
            zengl_extras.init(gpu=True, opengl_core=False)
                app.run()