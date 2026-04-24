"""
Cross-Platform Save Data System for Witch's Weapon.
Ensures saves are portable across platforms and backward-compatible.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class SaveDataVersion:
    """Semantic versioning for save data."""
    CURRENT = "2.0.0"  # Major.Minor.Patch
    
    COMPATIBILITY_MATRIX = {
        "2.0.0": ["1.5.0", "1.4.0"],  # 2.0.0 can load these versions
        "1.5.0": ["1.4.0"],
        "1.4.0": []
    }


@dataclass
class PlatformMetadata:
    """Platform information embedded in save."""
    platform_name: str  # "web", "mobile_ios", "pc_windows", "console_switch", etc.
    device_name: str  # "iPhone 15", "Windows PC", etc.
    last_modified_platform: str
    last_modified_time: float  # Timestamp
    play_time_seconds: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProgressionData:
    """Platform-agnostic player progression."""
    player_level: int
    exp: int
    exp_to_next: int
    
    # Weapons - all weapons shared across platforms
    weapons: Dict[str, Dict[str, Any]]
    
    # PvE progress
    pve_stages_completed: int
    pve_highest_difficulty: int
    
    # PvP progress (platform-specific ranking NOT stored here)
    pvp_matches_played: int
    pvp_wins: int
    
    # VN progress
    vn_nodes_completed: List[str]
    vn_flags: Dict[str, Any]
    
    # Daily missions
    daily_missions_state: Dict[str, Any]
    
    # Cosmetics
    cosmetics_owned: List[str]
    current_loadout: Dict[str, str]


@dataclass
class PlatformSpecificData:
    """Data that CAN be platform-specific (optional)."""
    pvp_rank: Optional[int] = None  # Only for ranked systems
    platform_achievements: Optional[List[str]] = None
    platform_custom_data: Optional[Dict[str, Any]] = None


@dataclass
class CrossPlatformSaveData:
    """Complete save data with platform agnosticity guaranteed."""
    save_version: str
    created_at: float
    progression: ProgressionData
    platform_metadata: PlatformMetadata
    platform_specific: Optional[PlatformSpecificData] = None
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "save_version": self.save_version,
            "created_at": self.created_at,
            "progression": asdict(self.progression),
            "platform_metadata": self.platform_metadata.to_dict(),
            "platform_specific": asdict(self.platform_specific) if self.platform_specific else None,
            "checksum": self.checksum
        }


class SaveDataManager:
    """Manages save data with cross-platform support."""

    def __init__(self):
        self.current_save: Optional[CrossPlatformSaveData] = None
    
    def create_new_save(
        self,
        platform_name: str,
        device_name: str
    ) -> CrossPlatformSaveData:
        """Create a new save file."""
        metadata = PlatformMetadata(
            platform_name=platform_name,
            device_name=device_name,
            last_modified_platform=platform_name,
            last_modified_time=datetime.now().timestamp(),
            play_time_seconds=0
        )
        
        progression = ProgressionData(
            player_level=1,
            exp=0,
            exp_to_next=100,
            weapons={},
            pve_stages_completed=0,
            pve_highest_difficulty=0,
            pvp_matches_played=0,
            pvp_wins=0,
            vn_nodes_completed=[],
            vn_flags={},
            daily_missions_state={},
            cosmetics_owned=[],
            current_loadout={}
        )
        
        save = CrossPlatformSaveData(
            save_version=SaveDataVersion.CURRENT,
            created_at=datetime.now().timestamp(),
            progression=progression,
            platform_metadata=metadata
        )
        
        self.current_save = save
        return save
    
    def load_save(self, save_dict: Dict[str, Any]) -> CrossPlatformSaveData:
        """Load save from dict with version compatibility."""
        version = save_dict.get("save_version", "1.0.0")
        
        # Check version compatibility
        if not self._is_version_compatible(version):
            raise ValueError(f"Save file version {version} is not compatible")
        
        # Perform migration if needed
        if version != SaveDataVersion.CURRENT:
            save_dict = self._migrate_save(save_dict, version)
        
        # Reconstruct save object
        metadata = PlatformMetadata(**save_dict["platform_metadata"])
        progression = ProgressionData(**save_dict["progression"])
        
        platform_specific = None
        if save_dict.get("platform_specific"):
            platform_specific = PlatformSpecificData(**save_dict["platform_specific"])
        
        save = CrossPlatformSaveData(
            save_version=save_dict["save_version"],
            created_at=save_dict["created_at"],
            progression=progression,
            platform_metadata=metadata,
            platform_specific=platform_specific,
            checksum=save_dict.get("checksum")
        )
        
        # Verify checksum
        if not self._verify_checksum(save):
            raise ValueError("Save file checksum mismatch (possible corruption)")
        
        self.current_save = save
        return save
    
    def _is_version_compatible(self, version: str) -> bool:
        """Check if version is compatible with current build."""
        if version == SaveDataVersion.CURRENT:
            return True
        
        compat_list = SaveDataVersion.COMPATIBILITY_MATRIX.get(SaveDataVersion.CURRENT, [])
        return version in compat_list
    
    def _migrate_save(self, save_dict: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Migrate save data from old version to current."""
        if from_version == "1.4.0":
            # 1.4.0 -> 1.5.0 -> 2.0.0
            save_dict = self._migrate_1_4_to_1_5(save_dict)
            save_dict = self._migrate_1_5_to_2_0(save_dict)
        elif from_version == "1.5.0":
            # 1.5.0 -> 2.0.0
            save_dict = self._migrate_1_5_to_2_0(save_dict)
        
        save_dict["save_version"] = SaveDataVersion.CURRENT
        return save_dict
    
    def _migrate_1_4_to_1_5(self, save_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from v1.4.0 to v1.5.0."""
        # Example: Add new field with default value
        if "daily_missions_state" not in save_dict.get("progression", {}):
            save_dict["progression"]["daily_missions_state"] = {}
        return save_dict
    
    def _migrate_1_5_to_2_0(self, save_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from v1.5.0 to v2.0.0."""
        # Example: Restructure platform metadata
        if "platform_metadata" not in save_dict:
            save_dict["platform_metadata"] = {
                "platform_name": "unknown",
                "device_name": "unknown",
                "last_modified_platform": "unknown",
                "last_modified_time": save_dict.get("created_at", 0),
                "play_time_seconds": 0
            }
        return save_dict
    
    def update_play_time(self, seconds: float):
        """Update play time."""
        if self.current_save:
            self.current_save.progression.play_time_seconds += int(seconds)
    
    def update_progression_unsafe(self, updates: Dict[str, Any]):
        """
        Directly update progression data.
        Called from platform-agnostic game logic.
        """
        if not self.current_save:
            return
        
        for key, value in updates.items():
            if hasattr(self.current_save.progression, key):
                setattr(self.current_save.progression, key, value)
    
    def mark_platform_modified(self, platform_name: str):
        """Mark save as modified on a platform."""
        if self.current_save:
            self.current_save.platform_metadata.last_modified_platform = platform_name
            self.current_save.platform_metadata.last_modified_time = datetime.now().timestamp()
    
    def compute_checksum(self, save: CrossPlatformSaveData) -> str:
        """Compute integrity checksum."""
        import hashlib
        save_json = json.dumps(save.to_dict(), sort_keys=True)
        return hashlib.sha256(save_json.encode()).hexdigest()
    
    def _verify_checksum(self, save: CrossPlatformSaveData) -> bool:
        """Verify save integrity."""
        if not save.checksum:
            return True  # No checksum to verify
        
        computed = self.compute_checksum(save)
        return computed == save.checksum
    
    def serialize(self) -> str:
        """Serialize current save to JSON string."""
        if not self.current_save:
            return "{}"
        
        save_dict = self.current_save.to_dict()
        save_dict["checksum"] = self.compute_checksum(self.current_save)
        return json.dumps(save_dict, indent=4)
    
    def deserialize(self, json_str: str) -> CrossPlatformSaveData:
        """Deserialize save from JSON string."""
        save_dict = json.loads(json_str)
        return self.load_save(save_dict)


# Global save manager instance
_save_manager: Optional[SaveDataManager] = None


def initialize_save_manager() -> SaveDataManager:
    """Initialize global save manager."""
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveDataManager()
    return _save_manager


def get_save_manager() -> SaveDataManager:
    """Get global save manager."""
    if _save_manager is None:
        raise RuntimeError("Save manager not initialized. Call initialize_save_manager() first.")
    return _save_manager
