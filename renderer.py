from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRect, QPointF
from config import Config
import math

class Renderer:
    def __init__(self, physics, animation):
        self.physics = physics
        self.animation = animation
        # Spidey Color Palette
        self.color_red = QColor("#E30022")
        self.color_blue = QColor("#001A9E")
        self.color_black = QColor("#000000")
        self.color_white = QColor("#FFFFFF")
        self.color_eye = QColor("#F0F0F0")

    def scene_bounds(self):
        left = int(self.physics.x)
        top = int(self.physics.y)
        
        w = h = Config.RENDER_SIZE

        right = left + w
        bottom = top + h

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
            
        # Character Position
        x = int(self.physics.x - offset_x)
        y = int(self.physics.y - offset_y)
        
        if self.physics.contact_surface == "floor":
            self._draw_shadow(painter, x, y)
            
        # Draw Procedural Spiderman
        self._draw_spiderman(painter, x, y)
            
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

    def _draw_spiderman(self, painter, x, y):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center of the character block
        cx = x + Config.RENDER_SIZE // 2
        cy = y + Config.RENDER_SIZE // 2
        
        # Facing logic
        if not self.animation.facing_right:
            painter.translate(cx * 2, 0)
            painter.scale(-1, 1)
        
        state = self.animation.current_state
        frame = self.animation.current_frame
        
        # Dynamic Animation Values
        bounce = math.sin(frame * 0.5) * 5 if state == "IDLE" else 0
        leg_angle = math.sin(frame * 0.8) * 30 if state in ["WALK", "RUN"] else 0
        if state == "RUN": leg_angle *= 1.5
        
        # Draw Limbs (Back)
        self._draw_limb(painter, cx, cy + 20 + bounce, 15 + leg_angle, "leg") # Back Leg
        self._draw_limb(painter, cx, cy - 10 + bounce, -45, "arm") # Back Arm (generic pose)

        # Draw Torso
        torso_rect = QRect(cx - 20, cy - 15 + bounce, 40, 50)
        painter.setPen(QPen(self.color_black, 2))
        painter.setBrush(self.color_blue)
        painter.drawRoundedRect(torso_rect, 15, 15)
        
        # Red Chest Piece / Vest
        painter.setBrush(self.color_red)
        painter.drawChord(torso_rect, 0 * 16, 180 * 16) # Top half red
        
        # Spider Symbol
        painter.setPen(QPen(self.color_black, 1))
        painter.setBrush(self.color_black)
        painter.drawEllipse(cx - 4, cy + bounce, 8, 10) # Symbol body
        
        # Draw Limbs (Front)
        self._draw_limb(painter, cx, cy + 20 + bounce, -15 - leg_angle, "leg") # Front Leg
        
        # Arm Pose based on State
        arm_angle = 45
        if state == "WEBSHOOT":
            arm_angle = -80 # Extended forward
            self._draw_web_effect(painter, cx + 20, cy - 5 + bounce)
        elif state == "SWING":
            arm_angle = -150 # Reaching up
        elif state in ["WALK", "RUN"]:
            arm_angle = math.sin(frame * 0.8 + math.pi) * 40
            
        self._draw_limb(painter, cx, cy - 10 + bounce, arm_angle, "arm") # Front Arm

        # Draw Head
        head_y = cy - 40 + bounce
        painter.setBrush(self.color_red)
        painter.setPen(QPen(self.color_black, 2))
        painter.drawEllipse(cx - 22, head_y, 44, 48)
        
        # Eyes
        self._draw_eyes(painter, cx, head_y + 20)
        
        painter.restore()

    def _draw_limb(self, painter, x, y, angle, type="arm"):
        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        
        painter.setPen(QPen(self.color_black, 2))
        if type == "arm":
            painter.setBrush(self.color_red)
            painter.drawRoundedRect(-6, 0, 12, 35, 5, 5) # Upper arm
            # Hand
            painter.setBrush(self.color_red)
            painter.drawEllipse(-8, 30, 16, 16)
        else:
            painter.setBrush(self.color_blue)
            painter.drawRoundedRect(-8, 0, 16, 40, 6, 6) # Thigh
            painter.setBrush(self.color_red)
            painter.drawRoundedRect(-9, 35, 18, 20, 4, 4) # Boot
            
        painter.restore()

    def _draw_eyes(self, painter, cx, y):
        # White eyes with black outline, classic Spiderman shape
        painter.save()
        painter.setPen(QPen(self.color_black, 3))
        painter.setBrush(self.color_white)
        
        # Left Eye (from character's perspective, so right for us if facing right)
        # Actually we just draw them symmetrically
        eye_path_r = QPainterPath()
        eye_path_r.moveTo(5, 0)
        eye_path_r.quadTo(20, -10, 18, 15)
        eye_path_r.quadTo(5, 12, 5, 0)
        
        eye_path_l = QPainterPath()
        eye_path_l.moveTo(-5, 0)
        eye_path_l.quadTo(-20, -10, -18, 15)
        eye_path_l.quadTo(-5, 12, -5, 0)
        
        painter.translate(cx, y)
        painter.drawPath(eye_path_r)
        painter.drawPath(eye_path_l)
        painter.restore()

    def _draw_web_effect(self, painter, x, y):
        painter.save()
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        # Simple web line shoot
        for i in range(3):
            angle = (i - 1) * 15
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            painter.drawLine(0, 0, 40, 0)
            painter.restore()
        painter.restore()

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

