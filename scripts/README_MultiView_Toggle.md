# Multi-View Image Generation Toggle Guide

This guide explains how to toggle multi-view image generation on and off for both PartPacker and the renderer in your CAD-Coder project.

## Overview

The multi-view image generation system provides flexible control over:
- **Multi-view generation**: Enable/disable creation of multiple views
- **PartPacker integration**: Toggle PartPacker image processing
- **Renderer integration**: Toggle CAD drawing style rendering
- **Composite images**: Control creation of multi-view composite drawings

## Quick Start

### 1. Basic Toggle Commands

```bash
# Toggle multi-view generation on/off
python multi_view_manager.py --toggle-multi-view

# Toggle PartPacker integration
python multi_view_manager.py --toggle-partpacker

# Toggle renderer integration
python multi_view_manager.py --toggle-renderer

# Show current configuration
python multi_view_manager.py --show-config
```

### 2. Using Preset Configurations

```bash
# Use minimal configuration (no multi-view)
python multi_view_manager.py --preset minimal

# Use standard configuration (renderer only)
python multi_view_manager.py --preset standard

# Use full configuration (everything enabled)
python multi_view_manager.py --preset full

# Use PartPacker only
python multi_view_manager.py --preset partpacker_only

# Use renderer only
python multi_view_manager.py --preset renderer_only
```

### 3. Custom Configuration

```bash
# Enable specific features
python multi_view_manager.py --enable-multi-view --enable-renderer

# Set specific views
python multi_view_manager.py --views isometric top side

# Set renderer style
python multi_view_manager.py --style technical

# Set composite layout
python multi_view_manager.py --layout grid
```

## Configuration Options

### Multi-View Settings

| Option | Description | Values |
|--------|-------------|---------|
| `enable_multi_view` | Enable/disable multi-view generation | `true`/`false` |
| `views` | Views to generate | `isometric`, `top`, `side`, `front`, `bottom` |
| `composite_layout` | Layout for composite images | `grid`, `horizontal`, `vertical` |

### PartPacker Settings

| Option | Description | Values |
|--------|-------------|---------|
| `enable_partpacker` | Enable/disable PartPacker integration | `true`/`false` |
| `partpacker_enable_3d` | Enable 3D model processing | `true`/`false` |
| `partpacker_enable_2d` | Enable 2D image processing | `true`/`false` |
| `partpacker_output_dir` | PartPacker output directory | Path string |

### Renderer Settings

| Option | Description | Values |
|--------|-------------|---------|
| `enable_renderer` | Enable/disable renderer integration | `true`/`false` |
| `renderer_style` | CAD drawing style | `technical`, `blueprint`, `modern` |
| `renderer_background` | Background color | Color name or RGB tuple |
| `renderer_line_width` | Line width for edges | Integer |

## Integration with CAD-Coder Workflow

### 1. Enhanced Model Generation

Use the enhanced generator with multi-view support:

```bash
# Basic usage with multi-view enabled
python enhanced_generate_model_cad.py \
    --dataset_name cadquery_test_data_subset100 \
    --model_tested CADCODER/CAD-Coder \
    --code_language cadquery \
    --pc_reps 3 \
    --parallel \
    --enable-multi-view \
    --enable-renderer \
    --views isometric top side front \
    --renderer-style technical
```

### 2. Using Configuration Files

Create a configuration file `my_config.json`:

```json
{
  "enable_multi_view": true,
  "enable_partpacker": false,
  "enable_renderer": true,
  "views": ["isometric", "top", "side", "front"],
  "composite_layout": "grid",
  "renderer_style": "technical",
  "image_resolution": [1024, 768],
  "output_dir": "./my_rendered_images"
}
```

Use the configuration:

```bash
# Load from file
python multi_view_manager.py --config my_config.json --process ./model_output

# Use with enhanced generator
python enhanced_generate_model_cad.py \
    --dataset_name cadquery_test_data_subset100 \
    --model_tested CADCODER/CAD-Coder \
    --code_language cadquery \
    --pc_reps 3 \
    --parallel \
    --multi-view-config my_config.json
```

## Preset Configurations

### Minimal
- Multi-view: ❌ Disabled
- PartPacker: ❌ Disabled
- Renderer: ❌ Disabled
- Views: `isometric` only

### Standard
- Multi-view: ✅ Enabled
- PartPacker: ❌ Disabled
- Renderer: ✅ Enabled
- Views: `isometric`, `top`, `side`, `front`
- Layout: `grid`

### Full
- Multi-view: ✅ Enabled
- PartPacker: ✅ Enabled
- Renderer: ✅ Enabled
- Views: `isometric`, `top`, `side`, `front`, `bottom`
- Layout: `grid`
- 3D/2D: Both enabled

### PartPacker Only
- Multi-view: ✅ Enabled
- PartPacker: ✅ Enabled
- Renderer: ❌ Disabled
- Views: `isometric`, `top`, `side`, `front`

### Renderer Only
- Multi-view: ✅ Enabled
- PartPacker: ❌ Disabled
- Renderer: ✅ Enabled
- Views: `isometric`, `top`, `side`, `front`
- Style: `technical`

## Advanced Usage

### 1. Programmatic Control

```python
from multi_view_manager import MultiViewManager
from config import MultiViewConfig

# Create custom configuration
config = MultiViewConfig(
    enable_multi_view=True,
    enable_renderer=True,
    enable_partpacker=False,
    views=['isometric', 'top', 'side'],
    renderer_style='blueprint'
)

# Initialize manager
manager = MultiViewManager(config)

# Toggle features
manager.toggle_partpacker(True)
manager.toggle_multi_view(False)

# Process CAD-Coder output
manager.process_cadcoder_output("./model_output")
```

### 2. Batch Processing

```bash
# Process multiple datasets with different configurations
for dataset in dataset1 dataset2 dataset3; do
    python enhanced_generate_model_cad.py \
        --dataset_name $dataset \
        --model_tested CADCODER/CAD-Coder \
        --code_language cadquery \
        --pc_reps 3 \
        --parallel \
        --enable-multi-view \
        --enable-renderer \
        --renderer-style technical
done
```

### 3. Conditional Processing

```python
# Process only if certain conditions are met
if model_has_valid_step_files:
    manager.toggle_renderer(True)
    manager.process_renderer_images(step_dir)
else:
    manager.toggle_renderer(False)
    print("Skipping renderer processing - no valid STEP files")
```

## File Structure

```
scripts/
├── config.py                    # Configuration management
├── multi_view_manager.py        # Main manager class
├── enhanced_generate_model_cad.py # Enhanced CAD generator
├── multi_view_to_single.py      # Legacy multi-view converter
└── README_MultiView_Toggle.md   # This file
```

## Output Structure

When multi-view generation is enabled:

```
inference/
├── rendered_images/             # Individual view images
│   ├── part_001/
│   │   ├── part_001_isometric.png
│   │   ├── part_001_top.png
│   │   ├── part_001_side.png
│   │   └── part_001_front.png
│   └── part_002/
│       └── ...
├── composite_images/            # Multi-view composites
│   ├── part_001_composite.png
│   ├── part_002_composite.png
│   └── ...
└── test_partpacker_images/      # PartPacker outputs (if enabled)
    └── ...
```

## Troubleshooting

### Common Issues

1. **Multi-view disabled but images still generated**
   - Check if `enable_multi_view` is set to `false`
   - Verify configuration is loaded correctly

2. **PartPacker integration not working**
   - Ensure PartPacker is installed and configured
   - Check `partpacker_output_dir` path exists

3. **Renderer integration fails**
   - Verify CadQuery and trimesh are installed
   - Check STEP files are valid

4. **Configuration not saved/loaded**
   - Ensure write permissions for config file
   - Check JSON syntax is valid

### Debug Commands

```bash
# Show current configuration
python multi_view_manager.py --show-config

# Test configuration loading
python multi_view_manager.py --config test_config.json --show-config

# Validate preset configurations
python multi_view_manager.py --preset standard --show-config
```

## Performance Considerations

### Optimization Tips

1. **Disable unused features**
   ```bash
   # For faster processing, disable unused features
   python multi_view_manager.py --preset minimal
   ```

2. **Reduce image resolution**
   ```python
   config.image_resolution = (400, 300)  # Lower resolution
   ```

3. **Limit views**
   ```bash
   # Generate only essential views
   python multi_view_manager.py --views isometric top
   ```

4. **Use parallel processing**
   ```bash
   # Enable parallel processing in enhanced generator
   python enhanced_generate_model_cad.py --parallel
   ```

### Memory Usage

- **PartPacker**: High memory usage for 3D models
- **Renderer**: Moderate memory usage per STEP file
- **Composite creation**: Low memory usage

## Integration Examples

### 1. Existing CAD-Coder Workflow

```bash
# Step 1: Generate model responses
./scripts/v1_5/eval/test_gencadcode.sh "CADCODER/CAD-Coder" "cadquery_test_data_subset100"

# Step 2: Generate CAD with multi-view images
python enhanced_generate_model_cad.py \
    --dataset_name cadquery_test_data_subset100 \
    --model_tested CADCODER/CAD-Coder \
    --code_language cadquery \
    --pc_reps 3 \
    --parallel \
    --enable-multi-view \
    --enable-renderer \
    --renderer-style technical

# Step 3: Compute IoU (unchanged)
python scripts/compute_iou.py --model_path CADCoder/CAD-Coder --test_set_name cadquery_test_data_subset100
```

### 2. Custom Workflow

```bash
# Create custom configuration
python multi_view_manager.py --preset full --save-config my_full_config.json

# Process with custom settings
python multi_view_manager.py \
    --config my_full_config.json \
    --process ./inference/inference_results/CAD-Coder/cadquery_test_data_subset100
```

## Future Enhancements

- **Dimension annotation**: Add dimension lines and text to rendered images
- **Custom lighting**: Advanced lighting configuration for renderer
- **Batch optimization**: Improved parallel processing for large datasets
- **Web interface**: GUI for configuration management
- **Integration APIs**: Direct integration with other CAD tools



