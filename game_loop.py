from PyQt5.QtCore import QTimer, Qt
from config import Config

class GameLoop:
    def __init__(self, app):
        self.app = app
        self.physics = app.physics
        self.animation = app.animation
        self.behavior = app.behavior
        
        # Setup Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000 // Config.FPS)

    def tick(self):
        # Update Logic
        dt = 1.0 / Config.FPS
        
        self.behavior.update(dt)
        self.physics.update(dt, self.behavior.current_state)
        self.animation.update(dt, self.physics.vx)
        self.app.sync_to_scene()
        
        # Trigger Repaint
        self.app.update()
        
    def start(self):
        self.timer.start()
        
    def stop(self):
        self.timer.stop()
