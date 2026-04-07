import math
import time
from config import Config
from utils.window_helper import WindowHelper

class PhysicsEngine:
    def __init__(self):
        starting_rect = Config.get_screen_available_rect(
            Config.VIRTUAL_LEFT + (Config.SCREEN_WIDTH // 2),
            Config.VIRTUAL_TOP + (Config.SCREEN_HEIGHT // 2),
        )
        self.x = starting_rect.left() + (starting_rect.width() - Config.RENDER_SIZE) / 2
        self.y = starting_rect.bottom() - Config.RENDER_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = True
        self.is_walled = False
        self.is_ceiling = False
        self.wall_side = None
        self.contact_surface = "floor"
        self.crawl_direction = -1
        
        # Window awareness
        self.window_helper = WindowHelper()
        self.start_time = time.time()
        
        # Swing state
        self.swing_anchor = (0, 0)
        self.swing_length = 0
        self.swing_angle = 0
        self.swing_angular_vel = 0

    def update(self, dt, current_state):
        frame_scale = dt / Config.TARGET_DT if Config.TARGET_DT else 1.0

        # Update window data
        self.window_helper.update(int((time.time() - self.start_time) * 1000))
        
        if current_state == "SWING":
            self._update_swing(frame_scale)
        else:
            self._update_linear(frame_scale, current_state)
            
        self._check_collisions()

    def _update_linear(self, frame_scale, state):
        # Apply Gravity
        if not self.is_grounded and state not in ["CRAWL", "SWING"]:
            self.vy += Config.GRAVITY * frame_scale
            if self.vy > Config.TERMINAL_VELOCITY:
                self.vy = Config.TERMINAL_VELOCITY

        # Update Position
        self.x += self.vx * frame_scale
        self.y += self.vy * frame_scale

    def _update_swing(self, frame_scale):
        if self.swing_length <= 0:
            self.swing_length = 1.0
            
        # Pendulum Physics: theta'' = -(g/L) * sin(theta)
        g = 0.5  # Local gravity scaling
        accel = -(g / self.swing_length) * math.sin(self.swing_angle)
        self.swing_angular_vel += accel * frame_scale
        self.swing_angular_vel *= 0.99 ** frame_scale
        self.swing_angle += self.swing_angular_vel * frame_scale

        # Cartesian from Polar
        self.x = self.swing_anchor[0] + self.swing_length * math.sin(self.swing_angle) - Config.RENDER_SIZE // 2
        self.y = self.swing_anchor[1] + self.swing_length * math.cos(self.swing_angle) - Config.RENDER_SIZE // 2
        
        # Linear velocities for when we release
        self.vx = self.swing_angular_vel * self.swing_length * math.cos(self.swing_angle)
        self.vy = -self.swing_angular_vel * self.swing_length * math.sin(self.swing_angle)

    def _check_collisions(self):
        screen_rect = Config.get_screen_available_rect(
            self.x + (Config.RENDER_SIZE / 2),
            self.y + (Config.RENDER_SIZE / 2),
        )
        
        # Get highest available ground (window/floor)
        ground_y = self.window_helper.get_ground_y(self.x, self.y, Config.RENDER_SIZE)
        ground_y = min(ground_y, screen_rect.bottom() - Config.RENDER_SIZE)
        
        # Ground check
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0
            self.is_grounded = True
            self.contact_surface = "floor"
        else:
            self.is_grounded = False

        # Wall check
        self.is_walled = False
        self.wall_side = None
        min_x = screen_rect.left()
        max_x = screen_rect.right() - Config.RENDER_SIZE
        if self.x <= min_x:
            self.x = min_x
            self.vx = 0
            self.is_walled = True
            self.wall_side = "left"
            self.contact_surface = "left_wall"
        elif self.x >= max_x:
            self.x = max_x
            self.vx = 0
            self.is_walled = True
            self.wall_side = "right"
            self.contact_surface = "right_wall"

        # Ceiling check
        min_y = screen_rect.top()
        if self.y <= min_y:
            self.y = min_y
            self.vy = 0
            self.is_ceiling = True
            self.contact_surface = "ceiling"
        else:
            self.is_ceiling = False

        if not self.is_grounded and not self.is_walled and not self.is_ceiling:
            self.contact_surface = "air"

    def jump(self):
        if self.is_grounded or self.is_walled or self.is_ceiling:
            self.vy = Config.JUMP_FORCE
            if self.wall_side == "left":
                self.vx = Config.WALK_SPEED * 1.5
            elif self.wall_side == "right":
                self.vx = -Config.WALK_SPEED * 1.5
            self.is_grounded = False
            self.is_ceiling = False
            self.is_walled = False
            self.contact_surface = "air"
            
    def start_swing(self):
        import random
        screen_rect = Config.get_screen_available_rect(
            self.x + (Config.RENDER_SIZE / 2),
            self.y + (Config.RENDER_SIZE / 2),
        )
        anchor_x = random.uniform(
            screen_rect.left() + (screen_rect.width() * 0.2),
            screen_rect.left() + (screen_rect.width() * 0.8),
        )
        self.swing_anchor = (anchor_x, screen_rect.top())
        
        dx = self.x + Config.RENDER_SIZE // 2 - anchor_x
        dy = self.y + Config.RENDER_SIZE // 2 - screen_rect.top()
        self.swing_length = max(1.0, math.sqrt(dx*dx + dy*dy))
        self.swing_angle = math.atan2(dx, dy)
        self.swing_angular_vel = self.vx / self.swing_length
