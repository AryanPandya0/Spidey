from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRect
import math

class SpidermanDesign:
    def __init__(self, render_size):
        self.render_size = render_size
        self.color_red = QColor("#E30022")
        self.color_blue = QColor("#001A9E")
        self.color_black = QColor("#000000")
        self.color_white = QColor("#FFFFFF")

    def draw(self, painter, x, y, animation):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center within the render block
        cx = x + self.render_size // 2
        cy = y + self.render_size // 2
        
        if not animation.facing_right:
            painter.translate(cx * 2, 0)
            painter.scale(-1, 1)
        
        state = animation.current_state
        frame = animation.current_frame
        
        # Procedural Animation Math
        bounce = math.sin(frame * 0.5) * 5 if state == "IDLE" else 0
        leg_angle = math.sin(frame * 0.8) * 30 if state in ["WALK", "RUN"] else 0
        if state == "RUN": leg_angle *= 1.5
        
        # Draw Sequence (Back to Front)
        self._draw_limb(painter, int(cx), int(cy + 20 + bounce), 15 + leg_angle, "leg")
        self._draw_limb(painter, int(cx), int(cy - 10 + bounce), -45, "arm")

        # Torso
        torso_rect = QRect(int(cx - 20), int(cy - 15 + bounce), 40, 50)
        painter.setPen(QPen(self.color_black, 2))
        painter.setBrush(self.color_blue)
        painter.drawRoundedRect(torso_rect, 15, 15)
        
        # Red Vest Detail
        painter.setBrush(self.color_red)
        painter.drawChord(torso_rect, 0, 180 * 16)
        
        # Spider Icon
        painter.setPen(QPen(self.color_black, 1))
        painter.setBrush(self.color_black)
        painter.drawEllipse(int(cx - 4), int(cy + bounce), 8, 10)
        
        # Front Leg
        self._draw_limb(painter, int(cx), int(cy + 20 + bounce), -15 - leg_angle, "leg")
        
        # Dynamic Arm Posing
        arm_angle = 45
        if state == "WEBSHOOT":
            arm_angle = -80
            self._draw_web_effect(painter, int(cx + 20), int(cy - 5 + bounce))
        elif state == "SWING":
            arm_angle = -150
        elif state in ["WALK", "RUN"]:
            arm_angle = math.sin(frame * 0.8 + 3.14) * 40
            
        self._draw_limb(painter, int(cx), int(cy - 10 + bounce), arm_angle, "arm")

        # Head
        head_y = int(cy - 40 + bounce)
        painter.setBrush(self.color_red)
        painter.setPen(QPen(self.color_black, 2))
        painter.drawEllipse(int(cx - 22), head_y, 44, 48)
        self._draw_eyes(painter, int(cx), head_y + 20)
        
        painter.restore()

    def _draw_limb(self, painter, x, y, angle, l_type):
        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        painter.setPen(QPen(self.color_black, 2))
        
        if l_type == "arm":
            painter.setBrush(self.color_red)
            painter.drawRoundedRect(-6, 0, 12, 35, 5, 5)
            painter.drawEllipse(-8, 30, 16, 16)
        else: # leg
            painter.setBrush(self.color_blue)
            painter.drawRoundedRect(-8, 0, 16, 40, 6, 6)
            painter.setBrush(self.color_red)
            painter.drawRoundedRect(-9, 35, 18, 20, 4, 4)
            
        painter.restore()

    def _draw_eyes(self, painter, cx, y):
        painter.save()
        painter.setPen(QPen(self.color_black, 3))
        painter.setBrush(self.color_white)
        
        # Right Eye Path
        path_r = QPainterPath()
        path_r.moveTo(5, 0)
        path_r.quadTo(20, -10, 18, 15)
        path_r.quadTo(5, 12, 5, 0)
        
        # Left Eye Path
        path_l = QPainterPath()
        path_l.moveTo(-5, 0)
        path_l.quadTo(-20, -10, -18, 15)
        path_l.quadTo(-5, 12, -5, 0)
        
        painter.translate(cx, y)
        painter.drawPath(path_r)
        painter.drawPath(path_l)
        painter.restore()

    def _draw_web_effect(self, painter, x, y):
        painter.save()
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        for i in range(3):
            angle = (i - 1) * 15
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            painter.drawLine(0, 0, 40, 0)
            painter.restore()
        painter.restore()
