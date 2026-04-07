from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
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

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.scene_rect = None
        
        self.physics = PhysicsEngine()
        self.animation = AnimationManager()
        self.behavior = BehaviorEngine(self.physics, self.animation)
        self.interaction = InteractionSystem(self.behavior, self)
        self.renderer = Renderer(self.physics, self.animation)
        self.game_loop = None

        self.sync_to_scene(force=True)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self.scene_rect is not None:
            self.renderer.draw(painter, self.scene_rect.left(), self.scene_rect.top())
        painter.end()

    def mousePressEvent(self, event):
        self.interaction.handle_mouse_press(event)

    def sync_to_scene(self, force=False):
        rect = self.renderer.scene_bounds()
        if force or self.scene_rect != rect:
            self.scene_rect = rect
            self.setGeometry(rect)

    def closeEvent(self, event):
        if self.game_loop is not None:
            self.game_loop.stop()
        super().closeEvent(event)
