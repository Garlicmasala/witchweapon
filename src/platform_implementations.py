"""
Platform Implementations for Witch's Weapon.
Concrete implementations of IPlatformProvider and IPlatformService for each platform.
"""

from src.platform_abstraction import (
    Platform, DeviceType, PlatformConfig, IPlatformProvider, IPlatformService
)
from src.input_system import IInputProvider, GameAction, InputEvent, AssistanceMode
from typing import Dict, List, Optional, Any, Set


# ============================================================================
# WEB PLATFORM
# ============================================================================

class WebPlatformProvider(IPlatformProvider):
    """Implementation for web (browser-based) platform."""

    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.dpi = 96.0

    def get_platform_config(self) -> PlatformConfig:
        return PlatformConfig(
            platform=Platform.WEB,
            device_type=DeviceType.WEB,
            supports_touch=True,
            supports_mouse=True,
            supports_controller=True,
            supports_vr=False,
            target_fps=60,
            performance_tier="medium",
            ui_mode="pointer"
        )

    def get_unique_device_id(self) -> str:
        return "web_" + self._get_browser_id()

    def _get_browser_id(self) -> str:
        """Get browser-based device ID (hashed for privacy)."""
        import hashlib
        user_agent = "mozilla"  # Would come from actual browser
        return hashlib.md5(user_agent.encode()).hexdigest()[:16]

    def get_device_name(self) -> str:
        return "Web Browser"

    def get_screen_width(self) -> int:
        return self.screen_width

    def get_screen_height(self) -> int:
        return self.screen_height

    def get_dpi(self) -> float:
        return self.dpi

    def is_online(self) -> bool:
        return True  # Assume web is always online


class WebInputProvider(IInputProvider):
    """Input provider for web (keyboard + mouse)."""

    def __init__(self):
        self.keys_held: Dict[str, bool] = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0

    def poll_input(self) -> list[InputEvent]:
        """Poll keyboard and mouse input, return abstract events."""
        events = []
        # In a real implementation, this would pull from browser input events
        # For now, return empty list
        return events

    def get_key_held(self, action: GameAction) -> float:
        """Get key held state (0.0-1.0)."""
        # In real implementation, would check DOM keyboard state
        return 0.0 if not self.keys_held.get(action.value, False) else 1.0

    def get_available_actions(self) -> Set[GameAction]:
        """Web supports all actions."""
        return set(GameAction)


class WebPlatformService(IPlatformService):
    """Platform services for web (mostly no-ops or localStorage)."""

    def __init__(self):
        self.purchases_allowed = False  # Might be disabled in web version

    def can_purchase(self) -> bool:
        return self.purchases_allowed

    def purchase_item(self, item_id: str, price_tier: str) -> bool:
        # Would redirect to payment provider
        return False

    def unlock_achievement(self, achievement_id: str) -> bool:
        # Would store in localStorage or send to server
        return True

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_friends(self) -> List[str]:
        return []

    def invite_friend(self, username: str) -> bool:
        return False

    def upload_save(self, save_data: Dict[str, Any]) -> bool:
        # Would send to server
        return True

    def download_save(self) -> Optional[Dict[str, Any]]:
        # Would fetch from server
        return None

    def get_last_sync_time(self) -> Optional[float]:
        return None

    def log_event(self, event_name: str, params: Dict[str, Any]) -> bool:
        # Would send to analytics server
        return True

    def set_user_property(self, key: str, value: Any) -> bool:
        return True

    def show_notification(self, title: str, message: str) -> bool:
        # Would use browser Notification API
        return True


# ============================================================================
# MOBILE PLATFORM (Android/iOS)
# ============================================================================

class MobilePlatformProvider(IPlatformProvider):
    """Base implementation for mobile platforms."""

    def __init__(self, is_ios: bool = False):
        self.is_ios = is_ios
        self.screen_width = 1080  # Typical mobile width
        self.screen_height = 2400
        self.dpi = 400.0  # Typical mobile DPI

    def get_platform_config(self) -> PlatformConfig:
        return PlatformConfig(
            platform=Platform.MOBILE_IOS if self.is_ios else Platform.MOBILE_ANDROID,
            device_type=DeviceType.MOBILE,
            supports_touch=True,
            supports_mouse=False,
            supports_controller=True,  # Can connect game controller
            supports_vr=False,
            target_fps=60,
            performance_tier="medium",
            ui_mode="touch"
        )

    def get_unique_device_id(self) -> str:
        # Would get from device API
        return "mobile_" + ("ios" if self.is_ios else "android") + "_12345"

    def get_device_name(self) -> str:
        return "iPhone 15" if self.is_ios else "Samsung Galaxy S24"

    def get_screen_width(self) -> int:
        return self.screen_width

    def get_screen_height(self) -> int:
        return self.screen_height

    def get_dpi(self) -> float:
        return self.dpi

    def is_online(self) -> bool:
        # Would check device connectivity
        return True


class MobileInputProvider(IInputProvider):
    """Input provider for mobile (touch + optional gamepad)."""

    def __init__(self):
        self.touches: List[Dict[str, float]] = []
        self.gamepad_enabled = False

    def poll_input(self) -> list[InputEvent]:
        """Poll touch and gamepad input."""
        events = []
        # In real implementation, would decode touch events
        return events

    def get_key_held(self, action: GameAction) -> float:
        # Mobile doesn't have continuous key hold in traditional sense
        return 0.0

    def get_available_actions(self) -> Set[GameAction]:
        """Mobile supports all actions except LOOK_HORIZONTAL (if no mouse)."""
        actions = set(GameAction)
        # Touch-based games typically don't have traditional look input
        # But can use gyro, so this depends on implementation
        return actions


class MobilePlatformService(IPlatformService):
    """Platform services for mobile (app store, cloud save, etc.)."""

    def __init__(self, is_ios: bool = False):
        self.is_ios = is_ios

    def can_purchase(self) -> bool:
        return True

    def purchase_item(self, item_id: str, price_tier: str) -> bool:
        # Would call App Store or Google Play API
        return True

    def unlock_achievement(self, achievement_id: str) -> bool:
        # Would call GameKit (iOS) or Google Play Games (Android)
        return True

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_friends(self) -> List[str]:
        # Would query Google Play Games or GameKit
        return []

    def invite_friend(self, username: str) -> bool:
        return False

    def upload_save(self, save_data: Dict[str, Any]) -> bool:
        # Would use Firebase or CloudKit
        return True

    def download_save(self) -> Optional[Dict[str, Any]]:
        return None

    def get_last_sync_time(self) -> Optional[float]:
        return None

    def log_event(self, event_name: str, params: Dict[str, Any]) -> bool:
        # Firebase Analytics
        return True

    def set_user_property(self, key: str, value: Any) -> bool:
        return True

    def show_notification(self, title: str, message: str) -> bool:
        # Native push notification
        return True


# ============================================================================
# PC PLATFORM (Windows/Mac/Linux)
# ============================================================================

class PcPlatformProvider(IPlatformProvider):
    """Base implementation for PC platforms."""

    def __init__(self, os_type: str = "windows"):
        self.os_type = os_type  # windows, mac, linux
        self.screen_width = 2560
        self.screen_height = 1440
        self.dpi = 96.0

    def get_platform_config(self) -> PlatformConfig:
        platform_map = {
            "windows": Platform.PC_WINDOWS,
            "mac": Platform.PC_MAC,
            "linux": Platform.PC_LINUX
        }
        return PlatformConfig(
            platform=platform_map.get(self.os_type, Platform.PC_WINDOWS),
            device_type=DeviceType.PC,
            supports_touch=False,
            supports_mouse=True,
            supports_controller=True,
            supports_vr=True,  # Some PC VR headsets
            target_fps=120,
            performance_tier="high",
            ui_mode="pointer"
        )

    def get_unique_device_id(self) -> str:
        return f"pc_{self.os_type}_" + self._get_machine_id()

    def _get_machine_id(self) -> str:
        """Get machine-specific ID (would come from OS)."""
        return "12345"

    def get_device_name(self) -> str:
        name_map = {"windows": "Windows PC", "mac": "Mac", "linux": "Linux PC"}
        return name_map.get(self.os_type, "PC")

    def get_screen_width(self) -> int:
        return self.screen_width

    def get_screen_height(self) -> int:
        return self.screen_height

    def get_dpi(self) -> float:
        return self.dpi

    def is_online(self) -> bool:
        return True


class PcInputProvider(IInputProvider):
    """Input provider for PC (keyboard + mouse + gamepad)."""

    def __init__(self):
        self.keys_held: Dict[str, bool] = {}
        self.mouse_x = 0
        self.mouse_y = 0

    def poll_input(self) -> list[InputEvent]:
        """Poll keyboard, mouse, and gamepad."""
        events = []
        # In real implementation, would pull from OS input APIs
        return events

    def get_key_held(self, action: GameAction) -> float:
        return 0.0 if not self.keys_held.get(action.value) else 1.0

    def get_available_actions(self) -> Set[GameAction]:
        """PC supports all actions."""
        return set(GameAction)


class PcPlatformService(IPlatformService):
    """Platform services for PC (Steam, Epic, Xbox App, etc.)."""

    def __init__(self, store: str = "steam"):
        self.store = store  # steam, epic, xbox, gog, etc.

    def can_purchase(self) -> bool:
        return True

    def purchase_item(self, item_id: str, price_tier: str) -> bool:
        # Would call Steam API, Epic API, etc.
        return True

    def unlock_achievement(self, achievement_id: str) -> bool:
        # Would call Steam Achievements, Epic Achievements, etc.
        return True

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_friends(self) -> List[str]:
        return []

    def invite_friend(self, username: str) -> bool:
        return False

    def upload_save(self, save_data: Dict[str, Any]) -> bool:
        # Would use Steam Cloud, Epic Cloud, etc.
        return True

    def download_save(self) -> Optional[Dict[str, Any]]:
        return None

    def get_last_sync_time(self) -> Optional[float]:
        return None

    def log_event(self, event_name: str, params: Dict[str, Any]) -> bool:
        # Would use Steam Events or similar
        return True

    def set_user_property(self, key: str, value: Any) -> bool:
        return True

    def show_notification(self, title: str, message: str) -> bool:
        # Would use OS notification API
        return True


# ============================================================================
# CONSOLE PLATFORM (Switch/PS5/Xbox)
# ============================================================================

class ConsolePlatformProvider(IPlatformProvider):
    """Base implementation for console platforms."""

    def __init__(self, console_type: str = "switch"):
        self.console_type = console_type  # switch, ps5, xbox
        self.screen_width = 1920 if console_type in ["ps5", "xbox"] else 1280
        self.screen_height = 1080
        self.dpi = 96.0

    def get_platform_config(self) -> PlatformConfig:
        platform_map = {
            "switch": Platform.CONSOLE_SWITCH,
            "ps5": Platform.CONSOLE_PS5,
            "xbox": Platform.CONSOLE_XBOX
        }
        return PlatformConfig(
            platform=platform_map.get(self.console_type, Platform.CONSOLE_SWITCH),
            device_type=DeviceType.CONSOLE,
            supports_touch=False,
            supports_mouse=False,
            supports_controller=True,
            supports_vr=False,
            target_fps=60,
            performance_tier="high",
            ui_mode="selection"
        )

    def get_unique_device_id(self) -> str:
        return f"console_{self.console_type}_" + "serial123"

    def get_device_name(self) -> str:
        name_map = {"switch": "Nintendo Switch", "ps5": "PlayStation 5", "xbox": "Xbox Series X"}
        return name_map.get(self.console_type, "Console")

    def get_screen_width(self) -> int:
        return self.screen_width

    def get_screen_height(self) -> int:
        return self.screen_height

    def get_dpi(self) -> float:
        return self.dpi

    def is_online(self) -> bool:
        return True


class ConsoleInputProvider(IInputProvider):
    """Input provider for console (controller only)."""

    def __init__(self):
        self.controller_state: Dict[str, float] = {}

    def poll_input(self) -> list[InputEvent]:
        """Poll controller input."""
        events = []
        return events

    def get_key_held(self, action: GameAction) -> float:
        return self.controller_state.get(action.value, 0.0)

    def get_available_actions(self) -> Set[GameAction]:
        """Console supports all controller-based actions."""
        return set(GameAction)


class ConsolePlatformService(IPlatformService):
    """Platform services for console (PSN, Xbox Live, Nintendo Switch Online)."""

    def __init__(self, console_type: str = "switch"):
        self.console_type = console_type

    def can_purchase(self) -> bool:
        return True

    def purchase_item(self, item_id: str, price_tier: str) -> bool:
        return True

    def unlock_achievement(self, achievement_id: str) -> bool:
        # PSN Trophies, Xbox Achievements, Switch Achievements
        return True

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        return None

    def get_friends(self) -> List[str]:
        return []

    def invite_friend(self, username: str) -> bool:
        return False

    def upload_save(self, save_data: Dict[str, Any]) -> bool:
        return True

    def download_save(self) -> Optional[Dict[str, Any]]:
        return None

    def get_last_sync_time(self) -> Optional[float]:
        return None

    def log_event(self, event_name: str, params: Dict[str, Any]) -> bool:
        return True

    def set_user_property(self, key: str, value: Any) -> bool:
        return True

    def show_notification(self, title: str, message: str) -> bool:
        return True
