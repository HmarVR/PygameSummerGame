import os

import pygame as pg

class AnimationManager:
    def __init__(self):
        self.images = {}
        
    def add_image(self, image: pg.Surface, id: int):
        self.images[id] = image

    def load_images_from_directory(self, path, folder):
        for i, name in enumerate(os.listdir(os.path.join(path, folder))):
            img = pg.image.load(os.path.join(path, folder, name))

            self.images[i] = img

    def get_image(self, index):
        return self.images[index]