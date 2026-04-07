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

    def update(self, dt):
        self.state_timer += 16.67  # Approx 60fps ms per frame
        
        # Dispatch to state logic
        if self.current_state == "IDLE":
            self._update_idle()
        elif self.current_state == "WALK":
            self._update_move(speed=Config.WALK_SPEED)
        elif self.current_state == "RUN":
            self._update_move(speed=Config.RUN_SPEED)
        elif self.current_state == "JUMP":
            self._update_jump()
        elif self.current_state == "CRAWL":
            self._update_crawl()
        elif self.current_state == "SWING":
            self._update_swing()
        elif self.current_state == "INTERACT":
            self._update_interact()

        # Update animation state
        self.animation.set_state(self.current_state)

    def _change_state(self, new_state):
        if self.current_state == new_state: return
        self.current_state = new_state
        self.state_timer = 0
        self.next_state_time = random.uniform(2000, 5000)

    def _update_idle(self):
        self.physics.vx = 0
        if self.state_timer >= self.next_state_time:
            choices = ["WALK", "RUN", "JUMP", "SWING"]
            weights = [0.4, 0.2, 0.3, 0.1]
            self._change_state(random.choices(choices, weights=weights)[0])
            
    def _update_move(self, speed):
        # Ledge Detection: If moving forward would result in ground_y being lower, stop or jump
        next_x = self.physics.x + (1 if self.target_x > self.physics.x else -1) * speed
        next_ground_y = self.physics.window_helper.get_ground_y(next_x, self.physics.y, Config.RENDER_SIZE)
        
        # If ground drops more than 50px, consider it a ledge
        is_ledge = next_ground_y > self.physics.y + 50
        
        if is_ledge and self.physics.is_grounded:
            if random.random() < 0.2: # 20% chance to jump off ledge
                self._change_state("JUMP")
                return
            else:
                self._change_state("IDLE")
                self.target_x = self.physics.x
                return

        # Normal move towards target
        if self.state_timer == 0 or abs(self.physics.x - self.target_x) < 5:
            self.target_x = random.randint(0, Config.SCREEN_WIDTH - Config.RENDER_SIZE)
            
        direction = 1 if self.target_x > self.physics.x else -1
        self.physics.vx = direction * speed
        
        # Chance to idle or jump
        if random.random() < 0.01:
            self._change_state("IDLE")
        elif random.random() < 0.005:
            self._change_state("JUMP")

    def _update_jump(self):
        if self.state_timer < 50:
            self.physics.vx = 0
        elif self.state_timer < 100:
            self.physics.jump()
            self.physics.vx = random.uniform(-5, 5)
            
        if self.physics.is_grounded and self.state_timer > 200:
            self._change_state("IDLE")
        elif self.physics.is_walled:
            self._change_state("CRAWL")

    def _update_crawl(self):
        self.physics.vx = 0
        self.physics.vy = -Config.WALK_SPEED
        if self.physics.is_ceiling or self.state_timer > 3000:
            self._change_state("JUMP")

    def _update_swing(self):
        if self.state_timer < 50:
            self.physics.start_swing()
        if self.state_timer > 4000:
            self._change_state("JUMP")

    def _update_interact(self):
        self.physics.vx = 0
        if self.state_timer > 2000:
            self._change_state("IDLE")
            
    def force_interact(self):
        self._change_state("INTERACT")
