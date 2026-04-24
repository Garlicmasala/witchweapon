"""
Platform Abstraction Layer for Witch's Weapon.
Defines the interface for platform-independent game logic.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class Platform(Enum):
    """Supported platforms."""
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    PC_WINDOWS = "pc_windows"
    PC_MAC = "pc_mac"
    PC_LINUX = "pc_linux"
    CONSOLE_SWITCH = "console_switch"
    CONSOLE_PS5 = "console_ps5"
    CONSOLE_XBOX = "console_xbox"
    VR_META = "vr_meta"
    VR_VIVE = "vr_vive"


class DeviceType(Enum):
    """Device categories for abstraction."""
    MOBILE = "mobile"
    PC = "pc"
    CONSOLE = "console"
    VR = "vr"
    WEB = "web"


@dataclass
class PlatformConfig:
    """Configuration for a platform."""
    platform: Platform
    device_type: DeviceType
    supports_touch: bool
    supports_mouse: bool
    supports_controller: bool
    supports_vr: bool
    target_fps: int = 60
    performance_tier: str = "medium"  # low, medium, high, ultra
    ui_mode: str = "default"  # touch, pointer, selection


class IPlatformProvider:
    """
    Abstract platform provider.
    All platform-specific operations go through this interface.
    """

    def get_platform_config(self) -> PlatformConfig:
        """Get platform configuration."""
        raise NotImplementedError

    def get_unique_device_id(self) -> str:
        """Get non-identifying unique device ID for analytics."""
        raise NotImplementedError

    def get_device_name(self) -> str:
        """Get human-readable device name."""
        raise NotImplementedError

    def get_screen_width(self) -> int:
        """Get screen width in pixels."""
        raise NotImplementedError

    def get_screen_height(self) -> int:
        """Get screen height in pixels."""
        raise NotImplementedError

    def get_dpi(self) -> float:
        """Get screen DPI for responsive scaling."""
        raise NotImplementedError

    def is_online(self) -> bool:
        """Check if device is online."""
        raise NotImplementedError


class IPlatformService:
    """
    Abstract platform services.
    Gameplay code never directly calls platform APIs.
    """

    # Purchases
    def can_purchase(self) -> bool:
        """Check if platform allows purchases."""
        raise NotImplementedError

    def purchase_item(self, item_id: str, price_tier: str) -> bool:
        """Initiate purchase. Returns True if successful."""
        raise NotImplementedError

    # Achievements
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement."""
        raise NotImplementedError

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Get achievement info."""
        raise NotImplementedError

    # Friends & Social
    def get_friends(self) -> List[str]:
        """Get list of friend usernames."""
        raise NotImplementedError

    def invite_friend(self, username: str) -> bool:
        """Invite friend to game."""
        raise NotImplementedError

    # Cloud Saves
    def upload_save(self, save_data: Dict[str, Any]) -> bool:
        """Upload save to cloud."""
        raise NotImplementedError

    def download_save(self) -> Optional[Dict[str, Any]]:
        """Download save from cloud."""
        raise NotImplementedError

    def get_last_sync_time(self) -> Optional[float]:
        """Get timestamp of last save sync."""
        raise NotImplementedError

    # Analytics
    def log_event(self, event_name: str, params: Dict[str, Any]) -> bool:
        """Log analytics event."""
        raise NotImplementedError

    def set_user_property(self, key: str, value: Any) -> bool:
        """Set user property for analytics."""
        raise NotImplementedError

    # Platform Notifications
    def show_notification(self, title: str, message: str) -> bool:
        """Show platform notification."""
        raise NotImplementedError


class PlatformManager:
    """Central manager for platform abstraction."""

    def __init__(self, provider: IPlatformProvider, service: IPlatformService):
        self.provider = provider
        self.service = service
        self._config = provider.get_platform_config()

    @property
    def config(self) -> PlatformConfig:
        """Get platform configuration."""
        return self._config

    @property
    def platform(self) -> Platform:
        """Get current platform."""
        return self._config.platform

    @property
    def device_type(self) -> DeviceType:
        """Get device type."""
        return self._config.device_type

    def is_mobile(self) -> bool:
        """Check if running on mobile."""
        return self.device_type == DeviceType.MOBILE

    def is_pc(self) -> bool:
        """Check if running on PC."""
        return self.device_type == DeviceType.PC

    def is_console(self) -> bool:
        """Check if running on console."""
        return self.device_type == DeviceType.CONSOLE

    def is_vr(self) -> bool:
        """Check if running in VR."""
        return self.device_type == DeviceType.VR

    def is_web(self) -> bool:
        """Check if running on web."""
        return self.device_type == DeviceType.WEB

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        return {
            "platform": self._config.platform.value,
            "device_type": self._config.device_type.value,
            "device_name": self.provider.get_device_name(),
            "screen_width": self.provider.get_screen_width(),
            "screen_height": self.provider.get_screen_height(),
            "dpi": self.provider.get_dpi(),
            "is_online": self.provider.is_online(),
            "fps_target": self._config.target_fps,
            "performance_tier": self._config.performance_tier
        }


# Global platform manager instance
_platform_manager: Optional[PlatformManager] = None


def initialize_platform(provider: IPlatformProvider, service: IPlatformService):
    """Initialize the global platform manager."""
    global _platform_manager
    _platform_manager = PlatformManager(provider, service)


def get_platform_manager() -> PlatformManager:
    """Get the global platform manager."""
    if _platform_manager is None:
        raise RuntimeError("Platform not initialized. Call initialize_platform() first.")
    return _platform_manager
