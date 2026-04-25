"""
Performance Tier System for Witch's Weapon.
Scales graphics and AI based on device capability, not platform.
Gameplay remains identical across tiers.
"""

from enum import Enum
from dataclasses import dataclass, replace
from typing import Dict, Any


class PerformanceTier(Enum):
    """Performance tiers based on capability, not platform."""
    LOW = "low"          # 30 FPS, low-end mobile
    MEDIUM = "medium"    # 45-60 FPS, high-end mobile / Switch
    HIGH = "high"        # 60 FPS, PC / console
    ULTRA = "ultra"      # 60-120 FPS, high-end PC


@dataclass
class PerformanceProfiler:
    """Detects device capability and recommends tier."""
    
    @staticmethod
    def detect_performance_tier(
        available_memory_mb: int,
        available_gpu_memory_mb: int,
        cpu_cores: int,
        is_mobile: bool = False
    ) -> PerformanceTier:
        """
        Detect recommended performance tier based on device specifications.
        """
        # Mobile heuristics
        if is_mobile:
            if available_memory_mb < 2000 or available_gpu_memory_mb < 512:
                return PerformanceTier.LOW
            elif available_memory_mb < 4000 or available_gpu_memory_mb < 1500:
                return PerformanceTier.MEDIUM
            else:
                return PerformanceTier.HIGH
        
        # PC / Console heuristics
        if available_memory_mb < 4000:
            return PerformanceTier.MEDIUM
        elif available_memory_mb < 8000:
            return PerformanceTier.HIGH
        else:
            return PerformanceTier.ULTRA


@dataclass
class TierSettings:
    """Settings for a performance tier. Gameplay is unaffected."""
    tier: PerformanceTier
    
    # Rendering
    target_fps: int
    vfx_density: float  # 0.0-1.0, scales particle count
    shadow_quality: str  # off, low, medium, high, ultra
    animation_lod: int  # 0=lowest, 3=highest
    texture_resolution: str  # ultra, high, medium, low
    
    # Physics
    physics_update_rate: int  # Hz
    collision_detail: str  # simple, standard, detailed
    
    # AI
    enemy_ai_update_hz: int  # How often AI thinks
    max_enemies_simulated: int
    pathfinding_iterations: int
    
    # Combat
    combat_log_detail: bool  # Verbose combat logging
    
    # Streaming
    asset_streaming_enabled: bool
    max_loaded_cells: int

    def __post_init__(self):
        """Validate settings."""
        if not (0.0 <= self.vfx_density <= 1.0):
            raise ValueError("vfx_density must be 0.0-1.0")


# Default tier configurations
DEFAULT_TIER_SETTINGS = {
    PerformanceTier.LOW: TierSettings(
        tier=PerformanceTier.LOW,
        target_fps=30,
        vfx_density=0.3,
        shadow_quality="off",
        animation_lod=0,
        texture_resolution="low",
        physics_update_rate=30,
        collision_detail="simple",
        enemy_ai_update_hz=15,
        max_enemies_simulated=3,
        pathfinding_iterations=10,
        combat_log_detail=False,
        asset_streaming_enabled=True,
        max_loaded_cells=1
    ),
    PerformanceTier.MEDIUM: TierSettings(
        tier=PerformanceTier.MEDIUM,
        target_fps=60,
        vfx_density=0.6,
        shadow_quality="medium",
        animation_lod=1,
        texture_resolution="medium",
        physics_update_rate=60,
        collision_detail="standard",
        enemy_ai_update_hz=30,
        max_enemies_simulated=5,
        pathfinding_iterations=20,
        combat_log_detail=False,
        asset_streaming_enabled=True,
        max_loaded_cells=2
    ),
    PerformanceTier.HIGH: TierSettings(
        tier=PerformanceTier.HIGH,
        target_fps=60,
        vfx_density=0.85,
        shadow_quality="high",
        animation_lod=2,
        texture_resolution="high",
        physics_update_rate=60,
        collision_detail="detailed",
        enemy_ai_update_hz=60,
        max_enemies_simulated=8,
        pathfinding_iterations=50,
        combat_log_detail=True,
        asset_streaming_enabled=True,
        max_loaded_cells=3
    ),
    PerformanceTier.ULTRA: TierSettings(
        tier=PerformanceTier.ULTRA,
        target_fps=120,
        vfx_density=1.0,
        shadow_quality="ultra",
        animation_lod=3,
        texture_resolution="ultra",
        physics_update_rate=120,
        collision_detail="detailed",
        enemy_ai_update_hz=120,
        max_enemies_simulated=10,
        pathfinding_iterations=100,
        combat_log_detail=True,
        asset_streaming_enabled=False,
        max_loaded_cells=5
    )
}


class PerformanceManager:
    """Manages performance tier and applies settings globally."""

    def __init__(self, initial_tier: PerformanceTier = PerformanceTier.MEDIUM):
        self.current_tier = initial_tier
        self.settings = replace(DEFAULT_TIER_SETTINGS[initial_tier])
        self.frametime_history = []
        self.max_history_length = 60  # Last 60 frames

    def set_tier(self, tier: PerformanceTier) -> None:
        """Change performance tier."""
        self.current_tier = tier
        self.settings = replace(DEFAULT_TIER_SETTINGS[tier])

    def get_tier(self) -> PerformanceTier:
        """Get current tier."""
        return self.current_tier

    def get_settings(self) -> TierSettings:
        """Get current tier settings."""
        return self.settings

    def record_frame_time(self, delta_time_ms: float) -> None:
        """Record frame time for adaptive scaling."""
        self.frametime_history.append(delta_time_ms)
        if len(self.frametime_history) > self.max_history_length:
            self.frametime_history.pop(0)

    def get_average_frame_time(self) -> float:
        """Get average frame time in milliseconds."""
        if not self.frametime_history:
            return 0.0
        return sum(self.frametime_history) / len(self.frametime_history)

    def get_fps(self) -> float:
        """Get current FPS."""
        avg_time = self.get_average_frame_time()
        if avg_time <= 0:
            return 0.0
        return 1000.0 / avg_time

    def auto_adjust_if_needed(self) -> None:
        """Automatically adjust tier if performance is poor."""
        fps = self.get_fps()
        target_fps = self.settings.target_fps
        
        # If consistently below 80% of target, drop tier
        if fps < target_fps * 0.8 and len(self.frametime_history) >= 30:
            if self.current_tier != PerformanceTier.LOW:
                tiers = [PerformanceTier.LOW, PerformanceTier.MEDIUM, PerformanceTier.HIGH, PerformanceTier.ULTRA]
                current_idx = tiers.index(self.current_tier)
                if current_idx > 0:
                    self.set_tier(tiers[current_idx - 1])

    def get_vfx_scale_factor(self) -> float:
        """Get VFX particle scaling factor."""
        return self.settings.vfx_density

    def get_shadow_quality(self) -> str:
        """Get shadow quality setting."""
        return self.settings.shadow_quality

    def get_animation_lod(self) -> int:
        """Get animation level of detail (0=lowest, 3=highest)."""
        return self.settings.animation_lod

    def get_max_concurrent_enemies(self) -> int:
        """Get max simultaneously simulated enemies."""
        return self.settings.max_enemies_simulated

    def get_ai_update_hz(self) -> int:
        """Get AI decision update frequency (Hz)."""
        return self.settings.enemy_ai_update_hz

    def to_dict(self) -> Dict[str, Any]:
        """Serialize performance settings."""
        return {
            "tier": self.current_tier.value,
            "target_fps": self.settings.target_fps,
            "vfx_density": self.settings.vfx_density
        }
