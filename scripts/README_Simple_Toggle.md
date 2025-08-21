# Simple Multi-View Toggle

Just add `--enable-multi-view` or `--disable-multi-view` to your existing commands.

## Quick Usage

### Enable Multi-View Generation
```bash
python scripts/generate_model_cad.py \
    --dataset_name cadquery_test_data_subset100 \
    --model_tested CADCODER/CAD-Coder \
    --code_language cadquery \
    --pc_reps 3 \
    --parallel \
    --enable-multi-view
```

### Disable Multi-View Generation
```bash
python scripts/generate_model_cad.py \
    --dataset_name cadquery_test_data_subset100 \
    --model_tested CADCODER/CAD-Coder \
    --code_language cadquery \
    --pc_reps 3 \
    --parallel \
    --disable-multi-view
```

### Standalone Multi-View Generation
```bash
# Generate composites from existing images
python scripts/simple_multi_view_toggle.py --enable

# Disable multi-view generation
python scripts/simple_multi_view_toggle.py --disable
```

## What It Does

- **Enabled**: Creates 2x2 composite images from individual view images
- **Disabled**: Skips multi-view generation entirely
- **Simple**: Just one flag, no complex configuration

## Output

When enabled, creates composite images in `./inference/composite_images/`:
- `part_001_composite.png`
- `part_002_composite.png`
- etc.

That's it! No complex configuration, no presets, just a simple on/off switch.



