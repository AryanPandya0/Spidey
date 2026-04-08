import random
import math
from config import Config

class BehaviorEngine:
    def __init__(self, physics, animation):
        self.physics = physics
        self.animation = animation
        self.current_state = "IDLE"
        self.state_timer = 0
        self.next_state_time = random.uniform(Config.MIN_IDLE_TIME, Config.MAX_IDLE_TIME)
        self.target_x = physics.x
        self.crawl_entry_side = "left"

    def update(self, dt):
        self.state_timer += dt * 1000.0
        
        # Dispatch to state logic
        if self.current_state == "IDLE":
            self._update_idle()
        elif self.current_state in ["WALK", "RUN"]:
            self._update_move(speed=Config.WALK_SPEED if self.current_state == "WALK" else Config.RUN_SPEED)
        elif self.current_state == "JUMP":
            self._update_jump()
        elif self.current_state == "CRAWL":
            self._update_crawl()
        elif self.current_state == "SWING":
            self._update_swing()
        elif self.current_state == "INTERACT":
            self._update_interact()
        elif self.current_state == "DRAG":
            self._update_drag()
        elif self.current_state == "WEBSHOOT":
            self._update_webshoot()

        # Update animation state
        # When dragging, show the "jump" sprite as it looks like being picked up
        anim_state = "JUMP" if self.current_state == "DRAG" else self.current_state
        self.animation.set_state(anim_state)

    def _update_drag(self):
        # We don't do much here as InteractionSystem handles movement
        # but we reset the timer to stay in this state
        self.state_timer = 0

    def _change_state(self, new_state):
        if self.current_state == new_state: return
        self.current_state = new_state
        self.state_timer = 0
        self.next_state_time = random.uniform(2000, 5000)

    def _update_idle(self):
        self.physics.vx = 0
        if self.state_timer >= self.next_state_time:
            choices = ["WALK", "RUN", "JUMP", "SWING", "WEBSHOOT"]
            weights = [0.35, 0.15, 0.25, 0.1, 0.15]
            self._change_state(random.choices(choices, weights=weights)[0])

    def _update_webshoot(self):
        self.physics.vx = 0
        self.physics.vy = 0
        if self.state_timer >= Config.WEBSHOOT_MAX_TIME:
            self._change_state("IDLE")
            
    def _update_move(self, speed):
        # Ledge Detection
        next_x = self.physics.x + (1 if self.target_x > self.physics.x else -1) * speed
        next_ground_y = self.physics.window_helper.get_ground_y(next_x, self.physics.y, Config.RENDER_SIZE)
        
        is_ledge = next_ground_y > self.physics.y + 100
        
        if is_ledge and self.physics.is_grounded:
            if random.random() < 0.2:
                self._change_state("JUMP")
                return
            else:
                self._change_state("IDLE")
                self.target_x = self.physics.x
                return

        # Target movement
        if abs(self.physics.x - self.target_x) < 10:
            screen_rect = Config.get_screen_available_rect(self.physics.x, self.physics.y)
            self.target_x = random.uniform(screen_rect.left(), screen_rect.right() - Config.RENDER_SIZE)
            
        direction = 1 if self.target_x > self.physics.x else -1
        self.physics.vx = direction * speed
        
        # State transitions
        if random.random() < 0.01:
            self._change_state("IDLE")

    def _update_jump(self):
        if self.state_timer < 50:
            self.physics.vx = 0
        elif self.state_timer < 100:
            self.physics.jump()
            self.physics.vx = random.uniform(-3, 3)
            
        if self.physics.is_grounded and self.state_timer > 300:
            self._change_state("IDLE")
        elif self.physics.is_walled or self.physics.is_ceiling:
            self.crawl_entry_side = self.physics.wall_side or "left"
            if self.physics.is_ceiling:
                self.physics.crawl_direction = -1 if self.crawl_entry_side == "right" else 1
            self._change_state("CRAWL")

    def _update_crawl(self):
        surface = self.physics.contact_surface

        if surface == "left_wall":
            self.physics.vx = 0
            self.physics.vy = -Config.WALK_SPEED
            self.animation.facing_right = True
        elif surface == "right_wall":
            self.physics.vx = 0
            self.physics.vy = -Config.WALK_SPEED
            self.animation.facing_right = False
        elif surface == "ceiling":
            self.physics.vx = self.physics.crawl_direction * Config.WALK_SPEED
            self.physics.vy = 0
            self.animation.facing_right = self.physics.crawl_direction > 0
        else:
            self._change_state("JUMP")
            return

        if self.state_timer > 4000:
            self._change_state("JUMP")

    def _update_swing(self):
        if self.state_timer <= (Config.TARGET_DT * 1000.0) + 1:
            self.physics.start_swing()
        if self.state_timer > 4000:
            self._change_state("JUMP")

    def _update_interact(self):
        self.physics.vx = 0
        if self.state_timer > 2000:
            self._change_state("IDLE")
            
    def force_interact(self):
        self._change_state("INTERACT")
