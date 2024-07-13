import pygame as pg
import numpy as np
from PIL import Image
import glm
import os, sys

from typing import TYPE_CHECKING

WEB = sys.platform in ("emscripten", "wasi")

if TYPE_CHECKING:
    from main import Game


class EventManager:
    def __init__(self, app: "Game") -> None:
        self.app = app
        self.app.share_data["event_manager"] = self
        
        self.just_pressed = []

    def handle_events(self, events):
        self.just_pressed = []
        for event in events:
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                if WEB:
                    pass
                else:
                    self.app.quit()

            if event.type == pg.WINDOWSIZECHANGED:
                self.app.WIN_SIZE = glm.ivec2(event.x, event.y)
                self.app.share_data["sizit"]()
                
            if (event.type == pg.KEYDOWN):
                self.just_pressed.append(event.key)
                
                if event.key == pg.K_F1:
                    if WEB:
                        pass
                    else:
                        default = self.app.mesh.vao.Framebuffers.framebuffers['default']
                        image_array = np.frombuffer(default.image_out[0].read(), dtype=np.uint8).reshape((480, 640, 4))
                        
                        pil_image = Image.fromarray(image_array)
                        pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip the image vertically
                        pil_image.save(f'screenshots/screenshot_{len(os.listdir("screenshots/"))}.png')  # SAVE IMAGE CODE
                elif event.key == pg.K_F2:
                    try: self.app.share_data["space_planet"].planet_manager.tp_planet()
                    except: pass
                    
                elif self.app.scene_manager.current_scene == "menu":
                    if event.key == pg.K_w:
                        self.app.share_data["main_menu"].move_selected(1)
                    elif event.key == pg.K_s:
                        self.app.share_data["main_menu"].move_selected(-1)
                    elif event.key == pg.K_e:
                        self.app.share_data["main_menu"].click()
                elif event.key == pg.K_e:
                    try: self.app.share_data["space_planet"].planet_manager.land_in_planet()
                    except: pass