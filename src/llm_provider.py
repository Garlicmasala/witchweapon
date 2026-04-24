"""
LLM Provider for Witch's Weapon.
Mock LLM with simple text generation, validation, and rate limiting.
"""

import time
import random

class LLMProvider:
    def __init__(self):
        self.last_request = 0
        self.rate_limit = 1  # 1 request per second
        self.responses = [
            "The winds of fate blow strongly today.",
            "Beware the shadows that lurk in the corners.",
            "Together we shall overcome any challenge.",
            "Magic flows through us all.",
            "Adventure awaits around every corner."
        ]

    def generate_response(self, prompt):
        """Generate a response with rate limiting."""
        current_time = time.time()
        if current_time - self.last_request < self.rate_limit:
            return "Rate limited. Please wait."
        self.last_request = current_time

        # Validate prompt (simple check)
        if "fantasy" not in prompt.lower() and "game" not in prompt.lower():
            return "Invalid prompt context."

        # Simple generation
        return random.choice(self.responses)
