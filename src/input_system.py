"""
Input Abstraction System for Witch's Weapon.
Maps platform-specific inputs to platform-agnostic actions.
"""

from enum import Enum
from typing import Dict, Callable, Optional, Any, Set
from dataclasses import dataclass


class GameAction(Enum):
    """Platform-agnostic game actions."""
    # Movement
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP = "move_up"  # For VR or vertical movement
    MOVE_DOWN = "move_down"
    
    # Rotation / Camera
    LOOK_HORIZONTAL = "look_horizontal"  # Mouse X, Right stick X
    LOOK_VERTICAL = "look_vertical"      # Mouse Y, Right stick Y
    
    # Combat
    ATTACK = "attack"
    DODGE = "dodge"
    JUMP = "jump"
    USE_SKILL = "use_skill"
    USE_ULTIMATE = "use_ultimate"
    SWITCH_WEAPON = "switch_weapon"
    
    # Targeting
    TOGGLE_TARGET = "toggle_target"
    CYCLE_TARGET_NEXT = "cycle_target_next"
    CYCLE_TARGET_PREVIOUS = "cycle_target_previous"
    
    # Interaction
    INTERACT = "interact"
    TALK = "talk"
    
    # Menu Navigation
    MENU_UP = "menu_up"
    MENU_DOWN = "menu_down"
    MENU_LEFT = "menu_left"
    MENU_RIGHT = "menu_right"
    MENU_CONFIRM = "menu_confirm"
    MENU_CANCEL = "menu_cancel"
    MENU_PAUSE = "menu_pause"
    
    # UI
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"


@dataclass
class InputEvent:
    """A platform-agnostic input event."""
    action: GameAction
    value: float  # 0.0-1.0 for analog, 1.0 for button
    is_pressed: bool  # True for press, False for release
    timestamp: float = 0.0


class IInputProvider:
    """
    Abstract input provider.
    Platform-specific implementations provide input via this interface.
    """

    def poll_input(self) -> list[InputEvent]:
        """
        Poll platform input and return abstract events.
        Called every frame.
        """
        raise NotImplementedError

    def get_key_held(self, action: GameAction) -> float:
        """Get current value of an action (0.0 = not held, 1.0 = fully held)."""
        raise NotImplementedError

    def get_available_actions(self) -> Set[GameAction]:
        """
        Get actions available on this platform.
        E.g., VR might not have LOOK_HORIZONTAL.
        """
        raise NotImplementedError


class InputMapper:
    """
    Maps platform-specific inputs to abstract game actions.
    """

    def __init__(self):
        self.action_callbacks: Dict[GameAction, list[Callable[[InputEvent], None]]] = {}
        self.continuous_callbacks: Dict[GameAction, list[Callable[[float], None]]] = {}

    def subscribe_action(
        self,
        action: GameAction,
        callback: Callable[[InputEvent], None]
    ) -> None:
        """Subscribe to discrete action events."""
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
        self.action_callbacks[action].append(callback)

    def subscribe_continuous(
        self,
        action: GameAction,
        callback: Callable[[float], None]
    ) -> None:
        """Subscribe to continuous analog input."""
        if action not in self.continuous_callbacks:
            self.continuous_callbacks[action] = []
        self.continuous_callbacks[action].append(callback)

    def process_input_event(self, event: InputEvent) -> None:
        """Process a platform input event."""
        if event.action in self.action_callbacks:
            for callback in self.action_callbacks[event.action]:
                callback(event)

    def process_continuous(self, action: GameAction, value: float) -> None:
        """Process continuous input."""
        if action in self.continuous_callbacks:
            for callback in self.continuous_callbacks[action]:
                callback(value)


class AssistanceMode(Enum):
    """Aiming/targeting assistance level."""
    OFF = "off"  # No assistance
    LIGHT = "light"  # Slight aim assist
    STRONG = "strong"  # Significant aim assist (mobile typical)
    FULL = "full"  # Full auto-target


@dataclass
class InputConfig:
    """Configuration for input handling."""
    # Assistance
    target_assistance: AssistanceMode = AssistanceMode.STRONG  # Mobile default
    aim_assist_strength: float = 0.7  # 0.0-1.0
    
    # Sensitivity (platform-agnostic)
    camera_sensitivity: float = 1.0
    movement_deadzone: float = 0.15
    
    # VR-specific
    use_snap_turn: bool = False
    snap_turn_angle: float = 45.0
    
    # Accessibility
    invert_camera_x: bool = False
    invert_camera_y: bool = False
    
    # Vibration/Haptics
    haptics_enabled: bool = True
    haptics_strength: float = 1.0


class InputSystem:
    """
    Central input system. Bridges platform input and game logic.
    Game logic only knows about GameActions.
    """

    def __init__(self, provider: IInputProvider):
        self.provider = provider
        self.mapper = InputMapper()
        self.config = InputConfig()
        self.last_frame_actions: Set[GameAction] = set()

    def update(self, delta_time: float) -> None:
        """Update input system. Call every frame."""
        current_frame_actions: Set[GameAction] = set()
        
        # Poll platform input
        events = self.provider.poll_input()
        for event in events:
            event.timestamp = delta_time
            self.mapper.process_input_event(event)
            
            if event.is_pressed:
                current_frame_actions.add(event.action)
        
        # Process continuous input
        available_actions = self.provider.get_available_actions()
        for action in available_actions:
            value = self.provider.get_key_held(action)
            if value > 0:
                self.mapper.process_continuous(action, value)
        
        self.last_frame_actions = current_frame_actions

    def get_action_was_pressed(self, action: GameAction) -> bool:
        """Check if action was pressed this frame."""
        return action in self.last_frame_actions

    def get_action_held(self, action: GameAction) -> float:
        """Get how much an analog action is being held (0.0-1.0)."""
        return self.provider.get_key_held(action)

    def apply_deadzone(self, value: float) -> float:
        """Apply deadzone to analog input."""
        deadzone = self.config.movement_deadzone
        if abs(value) < deadzone:
            return 0.0
        return (value - (deadzone if value > 0 else -deadzone)) / (1.0 - deadzone)

    def apply_camera_sensitivity(self, value: float) -> float:
        """Apply camera sensitivity multiplier."""
        return value * self.config.camera_sensitivity

    def set_assistance_mode(self, mode: AssistanceMode) -> None:
        """Change targeting assistance mode."""
        self.config.target_assistance = mode

    def get_assistance_mode(self) -> AssistanceMode:
        """Get current assistance mode."""
        return self.config.target_assistance
