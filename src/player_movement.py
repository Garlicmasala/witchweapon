"""
Player Movement for Witch's Weapon combat system.
Handles player positioning and movement mechanics in 3D space.
"""

class PlayerMovement:
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.position = [0, 0, 0]  # x, y, z

    def move(self, direction):
        # US: As a player, I want to move in the 3D game world to position for combat and interactions.
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
        self.ui.display_message(f"Player moved {direction} to position {self.position}")

    def get_position(self):
        return self.position.copy()