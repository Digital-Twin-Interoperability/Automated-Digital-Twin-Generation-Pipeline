#!/usr/bin/env python3
"""
Configuration file for CAD-Coder multi-view image generation settings.
This file allows you to toggle various image generation features on/off.
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class MultiViewConfig:
    """Configuration for multi-view image generation."""
    
    # Enable/disable multi-view generation
    enable_multi_view: bool = True
    
    # Enable/disable PartPacker integration
    enable_partpacker: bool = False
    
    # Enable/disable renderer integration
    enable_renderer: bool = True
    
    # Views to generate
    views: List[str] = None
    
    # Layout for composite images
    composite_layout: str = 'grid'  # 'grid', 'horizontal', 'vertical'
    
    # Image generation settings
    image_resolution: tuple = (800, 600)
    image_format: str = 'png'
    image_quality: int = 95
    
    # PartPacker specific settings
    partpacker_output_dir: str = "./inference/test_partpacker_images"
    partpacker_enable_3d: bool = True
    partpacker_enable_2d: bool = True
    
    # Renderer specific settings
    renderer_style: str = 'technical'  # 'technical', 'blueprint', 'modern'
    renderer_background: str = 'white'
    renderer_line_width: int = 2
    
    # Output directories
    output_dir: str = "./inference/rendered_images"
    composite_dir: str = "./inference/composite_images"
    
    def __post_init__(self):
        """Set default views if not specified."""
        if self.views is None:
            self.views = ['isometric', 'top', 'side', 'front']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'enable_multi_view': self.enable_multi_view,
            'enable_partpacker': self.enable_partpacker,
            'enable_renderer': self.enable_renderer,
            'views': self.views,
            'composite_layout': self.composite_layout,
            'image_resolution': self.image_resolution,
            'image_format': self.image_format,
            'image_quality': self.image_quality,
            'partpacker_output_dir': self.partpacker_output_dir,
            'partpacker_enable_3d': self.partpacker_enable_3d,
            'partpacker_enable_2d': self.partpacker_enable_2d,
            'renderer_style': self.renderer_style,
            'renderer_background': self.renderer_background,
            'renderer_line_width': self.renderer_line_width,
            'output_dir': self.output_dir,
            'composite_dir': self.composite_dir
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MultiViewConfig':
        """Create config from dictionary."""
        return cls(**config_dict)

# Default configuration
DEFAULT_CONFIG = MultiViewConfig()

# Configuration presets
CONFIG_PRESETS = {
    'minimal': MultiViewConfig(
        enable_multi_view=False,
        enable_partpacker=False,
        enable_renderer=False,
        views=['isometric']
    ),
    
    'standard': MultiViewConfig(
        enable_multi_view=True,
        enable_partpacker=False,
        enable_renderer=True,
        views=['isometric', 'top', 'side', 'front'],
        composite_layout='grid'
    ),
    
    'full': MultiViewConfig(
        enable_multi_view=True,
        enable_partpacker=True,
        enable_renderer=True,
        views=['isometric', 'top', 'side', 'front', 'bottom'],
        composite_layout='grid',
        partpacker_enable_3d=True,
        partpacker_enable_2d=True
    ),
    
    'partpacker_only': MultiViewConfig(
        enable_multi_view=True,
        enable_partpacker=True,
        enable_renderer=False,
        views=['isometric', 'top', 'side', 'front']
    ),
    
    'renderer_only': MultiViewConfig(
        enable_multi_view=True,
        enable_partpacker=False,
        enable_renderer=True,
        views=['isometric', 'top', 'side', 'front'],
        renderer_style='technical'
    )
}

def load_config(config_path: str = None) -> MultiViewConfig:
    """Load configuration from file or use default."""
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return MultiViewConfig.from_dict(config_dict)
    return DEFAULT_CONFIG

def save_config(config: MultiViewConfig, config_path: str):
    """Save configuration to file."""
    import json
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)

def get_preset_config(preset_name: str) -> MultiViewConfig:
    """Get a preset configuration."""
    if preset_name in CONFIG_PRESETS:
        return CONFIG_PRESETS[preset_name]
    else:
        raise ValueError(f"Unknown preset: {preset_name}. Available presets: {list(CONFIG_PRESETS.keys())}")

def print_config_summary(config: MultiViewConfig):
    """Print a summary of the current configuration."""
    print("🔧 Multi-View Image Generation Configuration:")
    print(f"  Multi-view enabled: {'✅' if config.enable_multi_view else '❌'}")
    print(f"  PartPacker enabled: {'✅' if config.enable_partpacker else '❌'}")
    print(f"  Renderer enabled: {'✅' if config.enable_renderer else '❌'}")
    print(f"  Views: {', '.join(config.views)}")
    print(f"  Composite layout: {config.composite_layout}")
    print(f"  Renderer style: {config.renderer_style}")
    print(f"  Output directory: {config.output_dir}")



