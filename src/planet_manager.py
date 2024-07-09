from typing import TYPE_CHECKING
from pygame import Vector2, image
import math
from copy import deepcopy
import struct
import webcolors

if TYPE_CHECKING:
    from main import Game
    from src.sun import Sun


# astral bodies
BODIES = {
    "Orion": {  # star
        "bodyRadius": 1000 / 4,
        "cloudRadius": 1050 / 4,
        "bodyPos": Vector2(16410, 5917),
        "lightDirection": [0.3, 0.6, -1.0],
        "isStar": True,
    },
    "Albasee": {
        "bodyRadius": 500 / 4,  # pixels
        "cloudRadius": 530 / 4,
        "bodyPos": Vector2(11_300, 27_450),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Vulakit": {
        "bodyRadius": 200 / 4,
        "cloudRadius": 250 / 4,
        "bodyPos": Vector2(9_000, 7_750),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Platee": {
        "bodyRadius": 330 / 4,
        "cloudRadius": 350 / 4,
        "bodyPos": Vector2(30083, 11523),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
}


class PlanetManager:
    def __init__(self, sun: "Sun", app: "Game") -> None:
        self.app = app
        self.sun = sun
        self.bodies = BODIES
        self.latest_planet = list(BODIES.keys())[0]

        self.load_palette()
        self.load_planet_textures()

        self.get_closest_planet()
        self.tp_planet()

    def load_planet_textures(self):
        self.planet_textures = {}
        for name, body in BODIES.items():
            tex = self.app.mesh.texture.get_texture(
                f"assets/textures/planets/{name.lower()}.png"
            ) # SO THAT TEXTURE.PY CAN DO GARBAGE COLLECTION BCUZ OGL != PYTHON
            
            self.app.mesh.texture.textures[name.lower()] = tex
            self.planet_textures[name.lower()] = tex

    def load_palette(self):
        _palette = """000000
21283f
38526e
3f86b0
839dbf
cee3ef
"""
        self.palette = []
        _palette = _palette.splitlines()
        palette_size = len(_palette)
        for v in _palette:
            rgb = webcolors.hex_to_rgb(v if v[0] == "#" else f"#{v}")
            color = [rgb.red / 255, rgb.green / 255, rgb.blue / 255, 1.0]  # rgba
            self.palette.append(color)

    def get_palette(self):
        buffer = bytearray()
        for rgb in self.palette:
            buffer.extend(struct.pack("ffff", *rgb))
        return buffer

    def get_planet_offset(self):
        # scrolls the planet(texture uv)
        return self.app.elapsed_time * self.time_speed * self.planetRotationSpeed

    def get_uniforms(self):
        self.time_speed = 1.0
        self.planetRotationSpeed = 0.01
        self.light_speed = 0.5

        return {
            "time": {
                "value": lambda: struct.pack("f", self.app.elapsed_time),
                "glsl_type": "float",
            },
            "planetCenter": {
                "value": lambda: struct.pack("ff", *self.planetPos),
                "glsl_type": "vec2",
            },
            "bodyRadius": {
                "value": lambda: struct.pack("f", self.bodyRadius),
                "glsl_type": "float",
            },
            "cloudRadius": {
                "value": lambda: struct.pack("f", self.cloudRadius),
                "glsl_type": "float",
            },
            "screenResolution": {
                "value": lambda: struct.pack("ff", *(640, 480)),
                "glsl_type": "vec2",
            },
            "aspectRatio": {
                "value": lambda: struct.pack(
                    "f", 4/3
                ),
                "glsl_type": "float",
            },
            "movedLightDirection": {
                "value": lambda: struct.pack(
                    "fff", *self.get_light_moved()
                ),  # TODO: actually code this
                "glsl_type": "vec3",
            },
            "paletteSize": {
                "value": lambda: struct.pack("i", len(self.palette)),
                "glsl_type": "int",
            },
            "palette": {
                "value": self.get_palette,
                "glsl_type": f"vec4[{len(self.palette)}]",
            },
            "time_speed": {
                "value": lambda: struct.pack("f", self.time_speed),
                "glsl_type": "float",
            },
            "planetRotationSpeed": {
                "value": lambda: struct.pack("f", self.planetRotationSpeed),
                "glsl_type": "float",
            },
            "planetOffset": {  # for rotating planet in X axis
                "value": lambda: struct.pack("f", self.get_planet_offset()),
                "glsl_type": "float",
            },
            "isStar": {
                "value": lambda: struct.pack(
                    "?", self.isStar
                ),  # TODO, make this a func
                "glsl_type": "bool",
            },
            "cameraPos": {
                "value": lambda: struct.pack(
                    "ff", self.app.camera.position.x, self.app.camera.position.y
                ),
                "glsl_type": "vec2",
            },
        }

    def dynamic_uniforms(self):
        past = deepcopy(self.latest_planet)
        self.get_closest_planet()
        if past != self.latest_planet:
            # moved to diff planet
            return self.get_uniforms()
        else:
            # same stuff, only update pos, light, texture scrolling
            body = self.bodies[self.latest_planet]
            cam_pos = Vector2(self.app.camera.position.x, self.app.camera.position.y)
            self.planetPos = body["bodyPos"] - cam_pos
            self.lightDirection = body["lightDirection"]
            updated = {
                "time": {
                    "value": lambda: struct.pack("f", self.app.elapsed_time),
                    "glsl_type": "float",
                },
                "planetCenter": {
                    "value": lambda: struct.pack("ff", *self.planetPos),
                    "glsl_type": "vec2",
                },
                "movedLightDirection": {
                    "value": lambda: struct.pack("fff", *self.get_light_moved()),
                    "glsl_type": "vec3",
                },
                "planetOffset": {  # for rotating planet in X axis
                    "value": lambda: struct.pack("f", self.get_planet_offset()),
                    "glsl_type": "float",
                },
            }
            return updated

    def get_light_moved(self):
        """
        startLightRot = 0.0
        rot = startLightRot - (
            self.app.elapsed_time * self.light_speed
        )  # between 0 and 2pi
        rot %= 2.0 * math.pi
        offset = (math.sin(rot) * 2.0, math.cos(rot) * 2.0)

        newLightDirection = deepcopy(self.lightDirection)

        newLightDirection[0] += offset[0]
        newLightDirection[2] += offset[1]
        """

        newLightDirection = [
            math.sin(self.app.elapsed_time),
            -0.6,
            math.cos(self.app.elapsed_time),
        ]

        return newLightDirection

    def get_closest_planet(self):
        past = deepcopy(self.latest_planet)
        # calculates uniforms for planet pos
        closest_dis = 999_999_999
        body_name = None
        cam_pos = Vector2(self.app.camera.position.x, self.app.camera.position.y)

        for name, body in BODIES.items():
            bodypos: Vector2 = body["bodyPos"]
            dis = cam_pos - bodypos
            if dis.length() < closest_dis:
                closest_dis = dis.length()
                body_name = name

        self.latest_planet = body_name
        body = BODIES[body_name]
        self.bodyRadius = body["bodyRadius"]
        self.cloudRadius = body["cloudRadius"]
        self.planetPos = body["bodyPos"] - cam_pos
        self.lightDirection = body["lightDirection"]
        self.isStar = body.get("isStar", False)
        self.has_changed_planet = True if self.latest_planet != body_name else False
        self.planet_id = list(BODIES.keys()).index(body_name)

        if past != self.latest_planet:
            self.sun.update_planet_tex(self.latest_planet)

    def tp_planet(self, id=None):
        if id == None:
            self.planet_id += 1
            self.planet_id %= len(BODIES.keys())
            planet = BODIES[list(BODIES.keys())[self.planet_id]]
            self.app.camera.position.x = planet["bodyPos"].x - 320
            self.app.camera.position.y = planet["bodyPos"].y - 240

    def land_in_planet(self):
        cam_pos = Vector2(self.app.camera.position.x + 320, self.app.camera.position.y + 240)
        body = BODIES[self.latest_planet]
        bodypos: Vector2 = deepcopy(body["bodyPos"])
        dis = cam_pos - bodypos
        if dis.length() <= body["bodyRadius"] + 100:
            self.app.scene_manager.load_scene('planet')
        print(dis.length())
