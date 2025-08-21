#!/usr/bin/env python3
"""
Multi-View Image Generation Manager for CAD-Coder
Handles PartPacker and renderer integration with toggle controls.
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import argparse

from config import MultiViewConfig, load_config, save_config, get_preset_config, print_config_summary

class MultiViewManager:
    """Manages multi-view image generation for CAD-Coder."""
    
    def __init__(self, config: MultiViewConfig = None):
        self.config = config or MultiViewConfig()
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary output directories."""
        if self.config.enable_multi_view:
            os.makedirs(self.config.output_dir, exist_ok=True)
            os.makedirs(self.config.composite_dir, exist_ok=True)
        
        if self.config.enable_partpacker:
            os.makedirs(self.config.partpacker_output_dir, exist_ok=True)
    
    def toggle_multi_view(self, enable: bool = None) -> bool:
        """Toggle multi-view generation on/off."""
        if enable is not None:
            self.config.enable_multi_view = enable
        else:
            self.config.enable_multi_view = not self.config.enable_multi_view
        
        print(f"Multi-view generation: {'✅ Enabled' if self.config.enable_multi_view else '❌ Disabled'}")
        return self.config.enable_multi_view
    
    def toggle_partpacker(self, enable: bool = None) -> bool:
        """Toggle PartPacker integration on/off."""
        if enable is not None:
            self.config.enable_partpacker = enable
        else:
            self.config.enable_partpacker = not self.config.enable_partpacker
        
        print(f"PartPacker integration: {'✅ Enabled' if self.config.enable_partpacker else '❌ Disabled'}")
        return self.config.enable_partpacker
    
    def toggle_renderer(self, enable: bool = None) -> bool:
        """Toggle renderer integration on/off."""
        if enable is not None:
            self.config.enable_renderer = enable
        else:
            self.config.enable_renderer = not self.config.enable_renderer
        
        print(f"Renderer integration: {'✅ Enabled' if self.config.enable_renderer else '❌ Disabled'}")
        return self.config.enable_renderer
    
    def set_views(self, views: List[str]):
        """Set which views to generate."""
        self.config.views = views
        print(f"Views set to: {', '.join(views)}")
    
    def set_composite_layout(self, layout: str):
        """Set composite image layout."""
        if layout in ['grid', 'horizontal', 'vertical']:
            self.config.composite_layout = layout
            print(f"Composite layout set to: {layout}")
        else:
            raise ValueError(f"Invalid layout: {layout}. Must be 'grid', 'horizontal', or 'vertical'")
    
    def set_renderer_style(self, style: str):
        """Set renderer style."""
        if style in ['technical', 'blueprint', 'modern']:
            self.config.renderer_style = style
            print(f"Renderer style set to: {style}")
        else:
            raise ValueError(f"Invalid style: {style}. Must be 'technical', 'blueprint', or 'modern'")
    
    def process_partpacker_images(self, input_dir: str = None) -> List[str]:
        """Process PartPacker generated images."""
        if not self.config.enable_partpacker:
            print("❌ PartPacker integration is disabled")
            return []
        
        input_dir = input_dir or self.config.partpacker_output_dir
        
        if not os.path.exists(input_dir):
            print(f"❌ PartPacker output directory not found: {input_dir}")
            return []
        
        print(f"🔄 Processing PartPacker images from: {input_dir}")
        
        # Find all image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(input_dir, '**', ext), recursive=True))
        
        if not image_files:
            print("❌ No image files found in PartPacker output directory")
            return []
        
        print(f"📸 Found {len(image_files)} image files")
        
        # Process images based on configuration
        processed_files = []
        
        for image_file in image_files:
            if self.config.partpacker_enable_2d:
                # Process 2D images
                processed_file = self._process_2d_image(image_file)
                if processed_file:
                    processed_files.append(processed_file)
            
            if self.config.partpacker_enable_3d:
                # Process 3D images (if any)
                processed_file = self._process_3d_image(image_file)
                if processed_file:
                    processed_files.append(processed_file)
        
        print(f"✅ Processed {len(processed_files)} PartPacker images")
        return processed_files
    
    def _process_2d_image(self, image_path: str) -> Optional[str]:
        """Process a 2D image from PartPacker."""
        try:
            # Load and resize image
            img = Image.open(image_path).convert('RGB')
            img = img.resize(self.config.image_resolution, Image.Resampling.LANCZOS)
            
            # Save to output directory
            filename = os.path.basename(image_path)
            output_path = os.path.join(self.config.output_dir, f"partpacker_2d_{filename}")
            img.save(output_path, format=self.config.image_format.upper(), quality=self.config.image_quality)
            
            return output_path
        except Exception as e:
            print(f"❌ Error processing 2D image {image_path}: {e}")
            return None
    
    def _process_3d_image(self, image_path: str) -> Optional[str]:
        """Process a 3D image from PartPacker."""
        # This would handle 3D model files (GLB, GLTF, etc.)
        # For now, just return None as placeholder
        return None
    
    def process_renderer_images(self, step_files_dir: str) -> List[str]:
        """Process STEP files using the renderer."""
        if not self.config.enable_renderer:
            print("❌ Renderer integration is disabled")
            return []
        
        if not os.path.exists(step_files_dir):
            print(f"❌ STEP files directory not found: {step_files_dir}")
            return []
        
        print(f"🔄 Processing STEP files from: {step_files_dir}")
        
        # Find all STEP files
        step_files = glob.glob(os.path.join(step_files_dir, "*.step"))
        
        if not step_files:
            print("❌ No STEP files found")
            return []
        
        print(f"📐 Found {len(step_files)} STEP files")
        
        # Import renderer if available
        try:
            from enhanced_cad_renderer import CADDrawingRenderer
            renderer = CADDrawingRenderer(
                background_color=self.config.renderer_background,
                line_width=self.config.renderer_line_width,
                resolution=self.config.image_resolution
            )
        except ImportError:
            print("❌ Enhanced CAD renderer not available. Install required dependencies.")
            return []
        
        processed_files = []
        
        for step_file in step_files:
            try:
                # Load STEP file
                import cadquery as cq
                solid = cq.importers.importStep(step_file)
                
                # Get part name
                part_name = os.path.splitext(os.path.basename(step_file))[0]
                
                # Create output directory for this part
                part_output_dir = os.path.join(self.config.output_dir, part_name)
                os.makedirs(part_output_dir, exist_ok=True)
                
                # Render all configured views
                rendered_files = []
                for view in self.config.views:
                    output_path = os.path.join(part_output_dir, f"{part_name}_{view}.{self.config.image_format}")
                    success = renderer.render_cad_view(
                        solid, output_path, view_type=view, style_name=self.config.renderer_style
                    )
                    if success:
                        rendered_files.append(output_path)
                
                # Create composite if multiple views were rendered
                if len(rendered_files) > 1 and self.config.enable_multi_view:
                    composite_path = os.path.join(part_output_dir, f"{part_name}_composite.{self.config.image_format}")
                    renderer.create_composite_drawing(rendered_files, composite_path, layout=self.config.composite_layout)
                    processed_files.append(composite_path)
                else:
                    processed_files.extend(rendered_files)
                
            except Exception as e:
                print(f"❌ Error processing STEP file {step_file}: {e}")
                continue
        
        print(f"✅ Processed {len(processed_files)} renderer images")
        return processed_files
    
    def create_composite_images(self, input_dir: str = None) -> List[str]:
        """Create composite images from individual view images."""
        if not self.config.enable_multi_view:
            print("❌ Multi-view generation is disabled")
            return []
        
        input_dir = input_dir or self.config.output_dir
        
        if not os.path.exists(input_dir):
            print(f"❌ Input directory not found: {input_dir}")
            return []
        
        print(f"🔄 Creating composite images from: {input_dir}")
        
        # Find all part directories
        part_dirs = []
        for item in os.listdir(input_dir):
            item_path = os.path.join(input_dir, item)
            if os.path.isdir(item_path):
                part_dirs.append(item)
        
        if not part_dirs:
            print("❌ No part directories found")
            return []
        
        composite_files = []
        
        for part_dir in part_dirs:
            part_path = os.path.join(input_dir, part_dir)
            
            # Find all images in the part directory
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(glob.glob(os.path.join(part_path, ext)))
            
            if len(image_files) >= 2:  # Need at least 2 images for composite
                # Sort images to ensure consistent order
                image_files.sort()
                
                # Create composite
                composite_path = os.path.join(self.config.composite_dir, f"{part_dir}_composite.{self.config.image_format}")
                success = self._create_composite_image(image_files, composite_path)
                if success:
                    composite_files.append(composite_path)
        
        print(f"✅ Created {len(composite_files)} composite images")
        return composite_files
    
    def _create_composite_image(self, image_paths: List[str], output_path: str) -> bool:
        """Create a composite image from multiple view images."""
        try:
            # Load all images
            images = []
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img = Image.open(img_path).convert('RGB')
                    images.append(img)
            
            if len(images) < 2:
                return False
            
            # Resize all images to the same size
            base_size = images[0].size
            resized_images = []
            for img in images:
                resized_img = img.resize(base_size, Image.Resampling.LANCZOS)
                resized_images.append(resized_img)
            
            # Create composite based on layout
            if self.config.composite_layout == 'grid':
                # 2x2 grid layout
                if len(resized_images) >= 4:
                    composite = Image.new('RGB', (base_size[0] * 2, base_size[1] * 2), 'white')
                    composite.paste(resized_images[0], (0, 0))  # Top-left
                    composite.paste(resized_images[1], (base_size[0], 0))  # Top-right
                    composite.paste(resized_images[2], (0, base_size[1]))  # Bottom-left
                    composite.paste(resized_images[3], (base_size[0], base_size[1]))  # Bottom-right
                else:
                    # Pad with white images
                    while len(resized_images) < 4:
                        white_img = Image.new('RGB', base_size, 'white')
                        resized_images.append(white_img)
                    composite = Image.new('RGB', (base_size[0] * 2, base_size[1] * 2), 'white')
                    composite.paste(resized_images[0], (0, 0))
                    composite.paste(resized_images[1], (base_size[0], 0))
                    composite.paste(resized_images[2], (0, base_size[1]))
                    composite.paste(resized_images[3], (base_size[0], base_size[1]))
            
            elif self.config.composite_layout == 'horizontal':
                # Horizontal layout
                composite = Image.new('RGB', (base_size[0] * len(resized_images), base_size[1]), 'white')
                for i, img in enumerate(resized_images):
                    composite.paste(img, (i * base_size[0], 0))
            
            elif self.config.composite_layout == 'vertical':
                # Vertical layout
                composite = Image.new('RGB', (base_size[0], base_size[1] * len(resized_images)), 'white')
                for i, img in enumerate(resized_images):
                    composite.paste(img, (0, i * base_size[1]))
            
            # Save composite
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            composite.save(output_path, format=self.config.image_format.upper(), quality=self.config.image_quality)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating composite image: {e}")
            return False
    
    def process_cadcoder_output(self, model_output_dir: str):
        """Process CAD-Coder model outputs with current configuration."""
        print("🚀 Processing CAD-Coder output with current configuration...")
        print_config_summary(self.config)
        
        # Process PartPacker images if enabled
        if self.config.enable_partpacker:
            self.process_partpacker_images()
        
        # Process renderer images if enabled
        if self.config.enable_renderer:
            step_dir = os.path.join(model_output_dir, "model_step")
            if os.path.exists(step_dir):
                self.process_renderer_images(step_dir)
            else:
                print(f"⚠️ STEP files directory not found: {step_dir}")
        
        # Create composite images if multi-view is enabled
        if self.config.enable_multi_view:
            self.create_composite_images()
        
        print("✅ CAD-Coder output processing complete!")
    
    def save_config(self, config_path: str = "./multi_view_config.json"):
        """Save current configuration to file."""
        save_config(self.config, config_path)
        print(f"💾 Configuration saved to: {config_path}")
    
    def load_config(self, config_path: str = "./multi_view_config.json"):
        """Load configuration from file."""
        self.config = load_config(config_path)
        self.setup_directories()
        print(f"📂 Configuration loaded from: {config_path}")
        print_config_summary(self.config)

def main():
    """Command line interface for MultiViewManager."""
    parser = argparse.ArgumentParser(description="Multi-View Image Generation Manager")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--preset", type=str, help="Use preset configuration", 
                       choices=['minimal', 'standard', 'full', 'partpacker_only', 'renderer_only'])
    parser.add_argument("--toggle-multi-view", action="store_true", help="Toggle multi-view generation")
    parser.add_argument("--toggle-partpacker", action="store_true", help="Toggle PartPacker integration")
    parser.add_argument("--toggle-renderer", action="store_true", help="Toggle renderer integration")
    parser.add_argument("--views", nargs='+', help="Set views to generate")
    parser.add_argument("--layout", type=str, choices=['grid', 'horizontal', 'vertical'], help="Set composite layout")
    parser.add_argument("--style", type=str, choices=['technical', 'blueprint', 'modern'], help="Set renderer style")
    parser.add_argument("--process", type=str, help="Process CAD-Coder output directory")
    parser.add_argument("--save-config", type=str, help="Save configuration to file")
    parser.add_argument("--show-config", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    # Initialize manager
    if args.preset:
        config = get_preset_config(args.preset)
        manager = MultiViewManager(config)
    elif args.config:
        manager = MultiViewManager()
        manager.load_config(args.config)
    else:
        manager = MultiViewManager()
    
    # Apply command line options
    if args.toggle_multi_view:
        manager.toggle_multi_view()
    
    if args.toggle_partpacker:
        manager.toggle_partpacker()
    
    if args.toggle_renderer:
        manager.toggle_renderer()
    
    if args.views:
        manager.set_views(args.views)
    
    if args.layout:
        manager.set_composite_layout(args.layout)
    
    if args.style:
        manager.set_renderer_style(args.style)
    
    # Show configuration
    if args.show_config:
        print_config_summary(manager.config)
    
    # Save configuration
    if args.save_config:
        manager.save_config(args.save_config)
    
    # Process CAD-Coder output
    if args.process:
        manager.process_cadcoder_output(args.process)

if __name__ == "__main__":
    main()



