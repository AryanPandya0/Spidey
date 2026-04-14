from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRect, QPoint
import math

class SpidermanDesign:
    def __init__(self, render_size):
        self.render_size = render_size
        
        # Premium Spidey Palette
        self.red = QColor("#D30000")
        self.red_light = QColor("#FF3131")
        self.red_dark = QColor("#8B0000")
        
        self.blue = QColor("#002366")
        self.blue_light = QColor("#003399")
        self.blue_dark = QColor("#000033")
        
        self.white = QColor("#FFFFFF")
        self.gray = QColor("#D3D3D3")
        self.black = QColor("#000000")
        self.web_color = QColor(0, 0, 0, 60) # Semi-transparent for webbing

    def draw(self, painter, x, y, animation):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, False) # Keep it crisp for pixel-style
        
        cx = x + self.render_size // 2
        cy = y + self.render_size // 2
        
        if not animation.facing_right:
            painter.translate(cx * 2, 0)
            painter.scale(-1, 1)
        
        state = animation.current_state
        frame = animation.current_frame
        
        # Motion Constants
        bounce = int(math.sin(frame * 0.5) * 4) if state == "IDLE" else 0
        leg_osc = math.sin(frame * 0.8)
        arm_osc = math.sin(frame * 0.8 + 3.14)
        
        # Scaling for "Pixel" look
        P = 4 # Pixel Size
        
        # 1. Back Limb (Z-Order)
        la = 15 + leg_osc * 30 if state in ["WALK", "RUN"] else 0
        self._draw_leg(painter, cx, cy + 5 * P + bounce, la, P, back=True)
        
        # 2. Torso & Arms Base
        self._draw_torso(painter, cx, cy + bounce, P)
        
        # 3. Front Leg
        la_f = -15 - leg_osc * 30 if state in ["WALK", "RUN"] else 0
        self._draw_leg(painter, cx, cy + 5 * P + bounce, la_f, P, back=False)
        
        # 4. Head (On Top)
        self._draw_head(painter, cx, cy - 8 * P + bounce, P)
        
        # 5. Front Arm
        aa = 45
        if state == "WEBSHOOT":
            aa = -100
            self._draw_web_effect(painter, int(cx + 6 * P), int(cy - 2 * P + bounce), P)
        elif state == "SWING":
            aa = -160
        elif state in ["WALK", "RUN"]:
            aa = arm_osc * 45
        self._draw_arm(painter, cx, cy - 2 * P + bounce, aa, P)
        
        painter.restore()

    def _draw_pixel_rect(self, painter, x, y, w, h, color, light_edge=False):
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawRect(int(x), int(y), int(w), int(h))
        
        if light_edge:
            painter.setBrush(QColor(255, 255, 255, 40))
            painter.drawRect(int(x), int(y), int(w), 2) # Top highlight

    def _draw_head(self, painter, cx, cy, P):
        painter.save()
        # Head Shape (Red)
        self._draw_pixel_rect(painter, cx - 4 * P, cy - 2 * P, 8 * P, 10 * P, self.red)
        # Rim Shading
        self._draw_pixel_rect(painter, cx + 3 * P, cy - 2 * P, 1 * P, 10 * P, self.red_dark)
        
        # Eyes (White with Black Border)
        # The iconic Sharp tilted Spidey eyes
        painter.setPen(QPen(self.black, 2))
        painter.setBrush(self.white)
        
        eye_path = QPainterPath()
        # Right Eye
        eye_path.moveTo(cx + 1 * P, cy + 1 * P)
        eye_path.lineTo(cx + 4.5 * P, cy - 1 * P)
        eye_path.lineTo(cx + 4 * P, cy + 4 * P)
        eye_path.closeSubpath()
        # Left Eye
        eye_path.moveTo(cx - 1 * P, cy + 1 * P)
        eye_path.lineTo(cx - 4.5 * P, cy - 1 * P)
        eye_path.lineTo(cx - 4 * P, cy + 4 * P)
        eye_path.closeSubpath()
        
        painter.drawPath(eye_path)
        
        # Subtle Webbing lines on head
        painter.setPen(QPen(self.web_color, 1))
        painter.drawLine(cx, cy - 2 * P, cx, cy + 8 * P)
        painter.drawLine(cx - 4 * P, cy + 3 * P, cx + 4 * P, cy + 3 * P)
        
        painter.restore()

    def _draw_torso(self, painter, cx, cy, P):
        # Blue Sides
        self._draw_pixel_rect(painter, cx - 5 * P, cy - 1 * P, 10 * P, 10 * P, self.blue)
        # Red Chest Piece (Vest shape)
        path = QPainterPath()
        path.moveTo(cx - 5 * P, cy - 1 * P)
        path.lineTo(cx + 5 * P, cy - 1 * P)
        path.lineTo(cx + 3 * P, cy + 9 * P)
        path.lineTo(cx - 3 * P, cy + 9 * P)
        path.closeSubpath()
        painter.setBrush(self.red)
        painter.setPen(QPen(self.black, 1))
        painter.drawPath(path)
        
        # Spider Emblem
        painter.setBrush(self.black)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 2, cy + 2 * P, 5, 7) # Body
        # Legs
        painter.setPen(QPen(self.black, 1))
        for i in range(4):
            y_off = i * 2
            painter.drawLine(cx - 2, cy + 2 * P + y_off, cx - 6, cy + 1 * P + y_off)
            painter.drawLine(cx + 2, cy + 2 * P + y_off, cx + 6, cy + 1 * P + y_off)

    def _draw_arm(self, painter, x, y, angle, P):
        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        
        # Shoulder (Red)
        self._draw_pixel_rect(painter, -2 * P, 0, 4 * P, 3 * P, self.red)
        # Lower Arm (Red)
        self._draw_pixel_rect(painter, -2 * P, 3 * P, 4 * P, 5 * P, self.red, light_edge=True)
        # Hand (Red)
        self._draw_pixel_rect(painter, -2.5 * P, 8 * P, 5 * P, 3 * P, self.red_dark)
        
        painter.restore()

    def _draw_leg(self, painter, x, y, angle, P, back=False):
        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        
        color = self.blue_dark if back else self.blue
        
        # Thigh (Blue)
        self._draw_pixel_rect(painter, -2.5 * P, 0, 5 * P, 6 * P, color)
        # Boot (Red)
        self._draw_pixel_rect(painter, -3 * P, 6 * P, 6 * P, 6 * P, self.red if not back else self.red_dark, light_edge=not back)
        # Foot
        self._draw_pixel_rect(painter, -3 * P, 12 * P, 8 * P, 2 * P, self.black if back else self.red_dark)
        
        painter.restore()

    def _draw_web_effect(self, painter, x, y, P):
        painter.save()
        painter.setPen(QPen(self.white, 2))
        for i in range(5):
            angle = (i - 2) * 12
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            painter.drawLine(0, 0, 50, 0)
            # Add some web "stickiness" bits
            painter.drawEllipse(20, -2, 4, 4)
            painter.restore()
        painter.restore()
