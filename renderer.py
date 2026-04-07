from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, QRect
from config import Config

class Renderer:
    def __init__(self, physics, animation):
        self.physics = physics
        self.animation = animation

    def scene_bounds(self):
        left = int(self.physics.x)
        top = int(self.physics.y)
        right = left + Config.RENDER_SIZE
        bottom = top + Config.RENDER_SIZE

        if self.animation.current_state == "SWING":
            ax, ay = self.physics.swing_anchor
            left = min(left, int(ax))
            top = min(top, int(ay))
            right = max(right, int(ax))
            bottom = max(bottom, int(ay))

        margin = Config.OVERLAY_MARGIN
        return QRect(
            left - margin,
            top - margin,
            (right - left) + margin * 2,
            (bottom - top) + margin * 2,
        )

    def draw(self, painter, offset_x=0, offset_y=0):
        # Draw Swing Rope
        if self.animation.current_state == "SWING":
            self._draw_rope(painter, offset_x, offset_y)
            
        # Draw Character
        sprite = self.animation.get_current_sprite()
        if sprite:
            x = int(self.physics.x - offset_x)
            y = int(self.physics.y - offset_y)
            self._draw_shadow(painter, x, y)
            painter.drawPixmap(x, y, sprite)
            
        # Draw Debug hitboxes
        if Config.DEBUG_MODE:
            self._draw_debug(painter, offset_x, offset_y)

    def _draw_shadow(self, painter, x, y):
        shadow_width = int(Config.RENDER_SIZE * 0.55)
        shadow_height = max(10, shadow_width // 5)
        shadow_x = x + (Config.RENDER_SIZE - shadow_width) // 2
        shadow_y = y + Config.RENDER_SIZE - shadow_height // 2
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
        painter.drawEllipse(shadow_x, shadow_y, shadow_width, shadow_height)

    def _draw_rope(self, painter, offset_x, offset_y):
        # Rope from anchor to character center
        pen = QPen(QColor("#E6EEF7"), 2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        
        ax, ay = self.physics.swing_anchor
        cx = self.physics.x + Config.RENDER_SIZE // 2 - offset_x
        cy = self.physics.y + Config.RENDER_SIZE // 2 - offset_y
        
        painter.drawLine(int(ax - offset_x), int(ay - offset_y), int(cx), int(cy))

    def _draw_debug(self, painter, offset_x, offset_y):
        # Hitbox
        pen = QPen(QColor("#00FF00"), 1)
        painter.setPen(pen)
        painter.drawRect(
            int(self.physics.x - offset_x),
            int(self.physics.y - offset_y),
            Config.RENDER_SIZE,
            Config.RENDER_SIZE,
        )
        
        # State Text
        painter.setPen(QColor("#00FF00"))
        painter.setFont(QFont("Consolas", 10))
        painter.drawText(
            int(self.physics.x - offset_x),
            int(self.physics.y - offset_y) - 5,
            self.animation.current_state,
        )
        
        # Physics Info
        info = f"Pos: {int(self.physics.x)},{int(self.physics.y)} Vel: {int(self.physics.vx)},{int(self.physics.vy)}"
        painter.drawText(
            int(self.physics.x - offset_x),
            int(self.physics.y - offset_y) + Config.RENDER_SIZE + 15,
            info,
        )
