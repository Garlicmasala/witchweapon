"""
Dialogue Manager for Witch's Weapon.
Handles scripted and dynamic dialogues with branches, cooldowns, and LLM integration.
"""

import time
import random

class DialogueManager:
    def __init__(self, ui_feedback, llm_provider):
        self.ui = ui_feedback
        self.llm = llm_provider
        self.active_dialogues = {}
        self.cooldowns = {}  # Character -> last dialogue time
        self.scripted_dialogues = {
            "companion1": {
                "greeting": ["Hello, adventurer!", "Ready for battle?"],
                "branches": {
                    "battle": ["Let's fight together!", "I'll support you."],
                    "rest": ["Take a break.", "Rest is important."]
                }
            }
        }

    def start_dialogue(self, speaker, listener):
        """Start a dialogue between speaker and listener."""
        dialogue_id = f"{speaker.name}_{listener.name}_{int(time.time())}"
        self.active_dialogues[dialogue_id] = {
            "speaker": speaker,
            "listener": listener,
            "state": "greeting",
            "branch": None,
            "cinematic_lock": False,  # Allow movement unless story
            "last_message": time.time()
        }
        self.display_message(speaker, "greeting")
        self.ui.display_message("Dialogue started. Type 'continue' to proceed, 'branch <option>' to choose, 'end' to stop.")

    def continue_dialogue(self, dialogue_id):
        """Continue the dialogue."""
        if dialogue_id not in self.active_dialogues:
            return
        dialogue = self.active_dialogues[dialogue_id]
        if dialogue["state"] == "greeting":
            dialogue["state"] = "waiting_branch"
        elif dialogue["state"] == "waiting_branch":
            # Use LLM for dynamic response if no branch
            if not dialogue["branch"]:
                self.dynamic_response(dialogue)
        # Allow player movement
        if not dialogue["cinematic_lock"]:
            self.ui.display_message("You can move while talking.")

    def choose_branch(self, dialogue_id, branch):
        """Choose a dialogue branch."""
        if dialogue_id not in self.active_dialogues:
            return
        dialogue = self.active_dialogues[dialogue_id]
        speaker = dialogue["speaker"]
        if branch in self.scripted_dialogues.get(speaker.name, {}).get("branches", {}):
            dialogue["branch"] = branch
            dialogue["state"] = "branched"
            self.display_message(speaker, branch)
        else:
            self.ui.display_message("Invalid branch.")

    def dynamic_response(self, dialogue):
        """Use LLM for dynamic dialogue."""
        speaker = dialogue["speaker"]
        prompt = f"Respond as {speaker.name} in a fantasy game context."
        response = self.llm.generate_response(prompt)
        self.ui.display_message(f"{speaker.name}: {response}")

    def display_message(self, speaker, key):
        """Display scripted message."""
        messages = self.scripted_dialogues.get(speaker.name, {}).get(key, ["..."])
        message = random.choice(messages)
        self.ui.display_message(f"{speaker.name}: {message}")

    def end_dialogue(self, dialogue_id):
        """End the dialogue."""
        if dialogue_id in self.active_dialogues:
            del self.active_dialogues[dialogue_id]
            self.ui.display_message("Dialogue ended.")

    def update_cooldowns(self):
        """Update dialogue cooldowns."""
        current_time = time.time()
        to_remove = []
        for char, last_time in self.cooldowns.items():
            if current_time - last_time > 30:  # 30 second cooldown
                to_remove.append(char)
        for char in to_remove:
            del self.cooldowns[char]
