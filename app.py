from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter
from config import Config
from physics import PhysicsEngine
from animation import AnimationManager
from behavior import BehaviorEngine
from interaction import InteractionSystem
from renderer import Renderer

class SpideyApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize Config
        Config.initialize()
        
        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        
        # Initialize Systems
        self.physics = PhysicsEngine()
        self.animation = AnimationManager()
        self.behavior = BehaviorEngine(self.physics, self.animation)
        self.interaction = InteractionSystem(self.behavior, self)
        self.renderer = Renderer(self.physics, self.animation)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        self.renderer.draw(painter)
        painter.end()

    def mousePressEvent(self, event):
        self.interaction.handle_mouse_press(event)

    def closeEvent(self, event):
        # Cleanup
        super().closeEvent(event)
