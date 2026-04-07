from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPoint
from config import Config

class Renderer:
    def __init__(self, physics, animation):
        self.physics = physics
        self.animation = animation

    def draw(self, painter):
        # Draw Swing Rope
        if self.animation.current_state == "SWING":
            self._draw_rope(painter)
            
        # Draw Character
        sprite = self.animation.get_current_sprite()
        if sprite:
            x, y = int(self.physics.x), int(self.physics.y)
            painter.drawPixmap(x, y, sprite)
            
        # Draw Debug hitboxes
        if Config.DEBUG_MODE:
            self._draw_debug(painter)

    def _draw_rope(self, painter):
        # Rope from anchor to character center
        pen = QPen(QColor("#FFFFFF"), 2, Qt.SolidLine)
        painter.setPen(pen)
        
        ax, ay = self.physics.swing_anchor
        cx = self.physics.x + Config.RENDER_SIZE // 2
        cy = self.physics.y + Config.RENDER_SIZE // 2
        
        painter.drawLine(int(ax), int(ay), int(cx), int(cy))

    def _draw_debug(self, painter):
        # Hitbox
        pen = QPen(QColor("#00FF00"), 1)
        painter.setPen(pen)
        painter.drawRect(int(self.physics.x), int(self.physics.y), Config.RENDER_SIZE, Config.RENDER_SIZE)
        
        # State Text
        painter.setPen(QColor("#00FF00"))
        painter.setFont(QFont("Consolas", 10))
        painter.drawText(int(self.physics.x), int(self.physics.y) - 5, self.animation.current_state)
        
        # Physics Info
        info = f"Pos: {int(self.physics.x)},{int(self.physics.y)} Vel: {int(self.physics.vx)},{int(self.physics.vy)}"
        painter.drawText(int(self.physics.x), int(self.physics.y) + Config.RENDER_SIZE + 15, info)
