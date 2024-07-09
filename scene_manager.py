import scenes.scene_loader as scene
    
    
class SceneManager():
    def __init__(self, app:"App") -> None:
        self.app = app
        self.scene = scene.GAMESCENES[scene.default_scene](self.app)
        self.current_scene = scene.default_scene
        self.pls_loadscene = False
        
    def update(self):
        self.scene.update()
        if self.pls_loadscene:
            self.scene.destroy()
            self.scene = self.newscene(self.app)
            self.pls_loadscene = False
        
    def load_scene(self, new_scene):
        self.pls_loadscene = True
        self.newscene = scene.GAMESCENES[new_scene]
        self.current_scene = new_scene