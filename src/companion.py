"""
Companion class for Witch's Weapon.
Handles companion characters with movement, follow behavior, and dialogue.
"""

import random
import time

class Companion:
    def __init__(self, name, ui_feedback, dialogue_manager):
        self.name = name
        self.ui = ui_feedback
        self.dialogue_manager = dialogue_manager
        self.position = [0, 0, 0]  # x, y, z
        self.follow_target = None
        self.idle_timer = 0
        self.last_interaction = 0
        self.affection = 0
        self.state = "idle"  # idle, following, interacting

    def set_position(self, pos):
        self.position = pos.copy()

    def get_position(self):
        return self.position.copy()

    def follow(self, target):
        """Start following a target (player or another character)."""
        self.follow_target = target
        self.state = "following"
        self.ui.display_message(f"{self.name} starts following.")

    def stop_following(self):
        self.follow_target = None
        self.state = "idle"
        self.ui.display_message(f"{self.name} stops following.")

    def update(self, delta_time=1.0):
        """Update companion behavior."""
        if self.state == "following" and self.follow_target:
            self.follow_behavior()
        elif self.state == "idle":
            self.idle_behavior(delta_time)

    def follow_behavior(self):
        """Follow the target with some distance."""
        target_pos = self.follow_target.get_position()
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        dz = target_pos[2] - self.position[2]
        distance = (dx**2 + dy**2 + dz**2)**0.5

        if distance > 2.0:  # Too far, move closer
            speed = 0.5
            self.position[0] += dx / distance * speed
            self.position[1] += dy / distance * speed
            self.position[2] += dz / distance * speed
        elif distance < 1.0:  # Too close, back off a bit
            speed = 0.2
            self.position[0] -= dx / distance * speed
            self.position[1] -= dy / distance * speed
            self.position[2] -= dz / distance * speed

    def idle_behavior(self, delta_time):
        """Perform idle/ambient movements."""
        self.idle_timer += delta_time
        if self.idle_timer > 5.0:  # Every 5 seconds, maybe move
            if random.random() < 0.3:  # 30% chance
                direction = random.choice(["up", "down", "left", "right", "forward", "back"])
                self.move(direction)
            self.idle_timer = 0

    def move(self, direction):
        """Move in a direction (2D plane for simplicity)."""
        if direction == "up":
            self.position[1] += 1
        elif direction == "down":
            self.position[1] -= 1
        elif direction == "left":
            self.position[0] -= 1
        elif direction == "right":
            self.position[0] += 1
        elif direction == "forward":
            self.position[2] += 1
        elif direction == "back":
            self.position[2] -= 1
        # Simulate gesture
        self.ui.display_message(f"{self.name} moves {direction} (gesture: walking).")

    def interact(self, player):
        """Check for proximity and initiate dialogue."""
        player_pos = player.get_position()
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        dz = player_pos[2] - self.position[2]
        distance = (dx**2 + dy**2 + dz**2)**0.5

        if distance < 3.0:  # Proximity trigger
            current_time = time.time()
            if current_time - self.last_interaction > 10:  # Cooldown
                self.face_to_face(player)
                self.dialogue_manager.start_dialogue(self, player)
                self.last_interaction = current_time
                self.state = "interacting"
            else:
                self.ui.display_message(f"{self.name} is on cooldown.")

    def face_to_face(self, player):
        """Simulate face-to-face orientation."""
        # Simple: just display message
        self.ui.display_message(f"{self.name} turns to face the player (face-to-face).")

    def gain_affection(self, amount):
        self.affection += amount
        if self.affection > 100:
            self.affection = 100
            self.position[2] -= 1
        # Simulate gesture
        self.ui.display_message(f"{self.name} moves {direction} (gesture: walking).")

    def interact(self, player):
        """Check for proximity and initiate dialogue."""
        player_pos = player.get_position()
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        dz = player_pos[2] - self.position[2]
        distance = (dx**2 + dy**2 + dz**2)**0.5

        if distance < 3.0:  # Proximity trigger
            current_time = time.time()
            if current_time - self.last_interaction > 10:  # Cooldown
                self.face_to_face(player)
                self.dialogue_manager.start_dialogue(self, player)
                self.last_interaction = current_time
                self.state = "interacting"
            else:
                self.ui.display_message(f"{self.name} is on cooldown.")

    def face_to_face(self, player):
        """Simulate face-to-face orientation."""
        # Simple: just display message
        self.ui.display_message(f"{self.name} turns to face the player (face-to-face).")

    def gain_affection(self, amount):
        self.affection += amount
        if self.affection > 100:
            self.affection = 100

    def check_interaction(self, player):
        """Check if player is close enough for interaction."""
        player_pos = player.position
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        dz = player_pos[2] - self.position[2]
        distance = (dx**2 + dy**2 + dz**2)**0.5
        if distance < 3.0:  # Interaction range
            current_time = time.time()
            if current_time - self.last_interaction > 10:  # Cooldown
                self.face_to_face(player)
                self.dialogue_manager.start_dialogue(self, player)
                self.last_interaction = current_time
                self.state = "interacting"
            else:
                self.ui.display_message(f"{self.name} is on cooldown.")

    def face_to_face(self, player):
        """Simulate face-to-face orientation."""
        # Simple: just display message
        self.ui.display_message(f"{self.name} turns to face the player (face-to-face).")

    def interact(self, player):
        """Handle interaction from player."""
        self.check_interaction(player)
