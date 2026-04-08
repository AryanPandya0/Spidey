from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from config import Config
from physics import PhysicsEngine
from animation import AnimationManager
from behavior import BehaviorEngine
from interaction import InteractionSystem
from renderer import Renderer
from utils.persistence_manager import PersistenceManager

class SpideyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            # Disabled WindowDoesNotAcceptFocus to allow mouse clicks
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.scene_rect = None
        
        self.persistence = PersistenceManager(Config.PERSISTENCE_PATH)
        self.physics = PhysicsEngine()
        
        # Load saved position
        saved_pos = self.persistence.get_pos()
        if saved_pos:
            self.physics.x = float(saved_pos.x())
            self.physics.y = float(saved_pos.y())

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

    def mouseMoveEvent(self, event):
        self.interaction.handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.interaction.handle_mouse_release(event)

    def sync_to_scene(self, force=False):
        rect = self.renderer.scene_bounds()
        if force or self.scene_rect != rect:
            self.scene_rect = rect
            self.setGeometry(rect)
        self.raise_()

    def closeEvent(self, event):
        if self.game_loop is not None:
            self.game_loop.stop()
        # Save position on exit
        if self.physics:
            self.persistence.save_pos(self.physics.x, self.physics.y)
        super().closeEvent(event)
