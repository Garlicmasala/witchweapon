"""
Responsive UI System for Witch's Weapon.
UI adapts to platform capabilities (touch, pointer, selection-based) and screen sizes.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any


class UIMode(Enum):
    """UI interaction modes based on platform."""
    TOUCH = "touch"        # Mobile: touchscreen
    POINTER = "pointer"    # PC: mouse/trackpad
    SELECTION = "selection"  # Console: D-pad/stick navigation
    VR = "vr"  # VR: 3D hand/gaze


class UIBreakpoint(Enum):
    """Responsive UI breakpoints based on screen size."""
    PHONE = "phone"        # < 600px
    TABLET = "tablet"      # 600px - 1200px
    DESKTOP = "desktop"    # > 1200px
    TV = "tv"  # Consoles


@dataclass
class LayoutConfig:
    """Layout configuration for a specific UI mode and breakpoint."""
    mode: UIMode
    breakpoint: UIBreakpoint
    
    # Sizing
    button_width: float  # pixels / percentage
    button_height: float
    padding: float
    gap_horizontal: float
    gap_vertical: float
    
    # Touch-specific
    min_touch_target: float = 44.0  # iOS guideline: 44x44
    
    # Text
    font_size_title: float = 32.0
    font_size_body: float = 16.0
    font_size_small: float = 12.0
    
    # Layout direction
    is_portrait_mode: bool = False


class UIResponsive:
    """Manages responsive UI layout based on platform."""

    def __init__(self):
        self.mode = UIMode.POINTER
        self.breakpoint = UIBreakpoint.DESKTOP
        self.screen_width = 1920
        self.screen_height = 1080
        self.layout_configs: Dict[tuple, LayoutConfig] = {}
        self._initialize_default_layouts()
        
    def _initialize_default_layouts(self):
        """Initialize default layout configurations."""
        # Touch - Phone
        self.layout_configs[(UIMode.TOUCH, UIBreakpoint.PHONE)] = LayoutConfig(
            mode=UIMode.TOUCH,
            breakpoint=UIBreakpoint.PHONE,
            button_width=0.9,  # 90% of screen width
            button_height=60,
            padding=16,
            gap_horizontal=10,
            gap_vertical=12,
            is_portrait_mode=True
        )
        
        # Touch - Tablet
        self.layout_configs[(UIMode.TOUCH, UIBreakpoint.TABLET)] = LayoutConfig(
            mode=UIMode.TOUCH,
            breakpoint=UIBreakpoint.TABLET,
            button_width=0.6,
            button_height=64,
            padding=20,
            gap_horizontal=15,
            gap_vertical=15,
            is_portrait_mode=False
        )
        
        # Pointer - Desktop
        self.layout_configs[(UIMode.POINTER, UIBreakpoint.DESKTOP)] = LayoutConfig(
            mode=UIMode.POINTER,
            breakpoint=UIBreakpoint.DESKTOP,
            button_width=200,
            button_height=40,
            padding=24,
            gap_horizontal=20,
            gap_vertical=12,
            min_touch_target=0  # Not touch-focused
        )
        
        # Selection - TV (Console)
        self.layout_configs[(UIMode.SELECTION, UIBreakpoint.TV)] = LayoutConfig(
            mode=UIMode.SELECTION,
            breakpoint=UIBreakpoint.TV,
            button_width=300,
            button_height=60,
            padding=32,
            gap_horizontal=24,
            gap_vertical=16,
            min_touch_target=0
        )
    
    def set_ui_mode(self, mode: UIMode):
        """Set UI interaction mode."""
        self.mode = mode
    
    def set_screen_size(self, width: int, height: int):
        """Update screen size and recalculate breakpoint."""
        self.screen_width = width
        self.screen_height = height
        self._update_breakpoint()
    
    def _update_breakpoint(self):
        """Update breakpoint based on screen width."""
        if self.screen_width < 600:
            self.breakpoint = UIBreakpoint.PHONE
        elif self.screen_width < 1200:
            self.breakpoint = UIBreakpoint.TABLET
        elif self.mode == UIMode.SELECTION:
            self.breakpoint = UIBreakpoint.TV
        else:
            self.breakpoint = UIBreakpoint.DESKTOP
    
    def get_layout(self) -> Optional[LayoutConfig]:
        """Get current layout configuration."""
        key = (self.mode, self.breakpoint)
        return self.layout_configs.get(key)
    
    def set_custom_layout(self, config: LayoutConfig):
        """Register a custom layout configuration."""
        key = (config.mode, config.breakpoint)
        self.layout_configs[key] = config


@dataclass
class MenuItemLayout:
    """Layout info for a menu item."""
    x: float
    y: float
    width: float
    height: float
    is_selectable: bool = True
    is_visible: bool = True


class ResponsiveMenu:
    """Base class for responsive menus."""

    def __init__(self, ui_responsive: UIResponsive):
        self.ui = ui_responsive
        self.items: List[Dict[str, Any]] = []
        self.selected_index = 0
    
    def add_item(self, item_id: str, label: str, **kwargs):
        """Add menu item."""
        self.items.append({
            "id": item_id,
            "label": label,
            **kwargs
        })
    
    def calculate_layout(self) -> List[MenuItemLayout]:
        """Calculate layout for all menu items."""
        layouts = []
        layout_config = self.ui.get_layout()
        
        if not layout_config:
            return layouts
        
        x = layout_config.padding
        y = layout_config.padding
        
        for item in self.items:
            width = layout_config.button_width
            if width < 1.0:  # Percentage
                width = self.ui.screen_width * width
            
            height = layout_config.button_height
            
            layout = MenuItemLayout(
                x=x,
                y=y,
                width=width,
                height=height
            )
            layouts.append(layout)
            
            y += height + layout_config.gap_vertical
        
        return layouts
    
    def handle_touch(self, touch_x: float, touch_y: float):
        """Handle touch input for touch mode."""
        if self.ui.mode != UIMode.TOUCH:
            return
        
        layouts = self.calculate_layout()
        for i, layout in enumerate(layouts):
            if (layout.x <= touch_x <= layout.x + layout.width and
                layout.y <= touch_y <= layout.y + layout.height):
                self.selected_index = i
                self._on_item_selected(i)
                break
    
    def handle_navigation(self, direction: str):
        """Handle D-pad/stick navigation for selection mode."""
        if self.ui.mode != UIMode.SELECTION:
            return
        
        if direction == "down":
            self.selected_index = min(self.selected_index + 1, len(self.items) - 1)
        elif direction == "up":
            self.selected_index = max(self.selected_index - 1, 0)
        elif direction == "confirm":
            self._on_item_selected(self.selected_index)
    
    def handle_mouse_click(self, mouse_x: float, mouse_y: float):
        """Handle mouse click for pointer mode."""
        if self.ui.mode != UIMode.POINTER:
            return
        
        layouts = self.calculate_layout()
        for i, layout in enumerate(layouts):
            if (layout.x <= mouse_x <= layout.x + layout.width and
                layout.y <= mouse_y <= layout.y + layout.height):
                self._on_item_selected(i)
                break
    
    def _on_item_selected(self, index: int):
        """Called when item is selected. Override in subclass."""
        pass


class UIServiceLocator:
    """
    Service locator for UI components.
    Provides platform-aware UI utilities.
    """

    def __init__(self, ui_responsive: UIResponsive):
        self.ui_responsive = ui_responsive
    
    def should_show_button_hints(self) -> bool:
        """Should UI show button labels/hints."""
        return self.ui_responsive.mode in [UIMode.TOUCH, UIMode.SELECTION]
    
    def should_use_confirmation_dialog(self) -> bool:
        """Should destructive actions show confirmation."""
        return self.ui_responsive.mode in [UIMode.SELECTION, UIMode.POINTER]
    
    def get_back_button_label(self) -> str:
        """Get appropriate back button label."""
        if self.ui_responsive.mode == UIMode.SELECTION:
            return "Back (B)"
        elif self.ui_responsive.mode == UIMode.TOUCH:
            return "← Back"
        else:
            return "Back"
    
    def get_confirm_button_label(self) -> str:
        """Get appropriate confirm button label."""
        if self.ui_responsive.mode == UIMode.SELECTION:
            return "Confirm (A)"
        elif self.ui_responsive.mode == UIMode.TOUCH:
            return "Tap to Confirm"
        else:
            return "Enter to Confirm"
    
    def get_minimum_button_size(self) -> tuple[int, int]:
        """Get minimum button size for accessibility."""
        if self.ui_responsive.mode == UIMode.TOUCH:
            return (44, 44)  # iOS guideline
        else:
            return (32, 32)
    
    def format_large_number(self, value: int) -> str:
        """Format large numbers appropriately for display."""
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        else:
            return str(value)
