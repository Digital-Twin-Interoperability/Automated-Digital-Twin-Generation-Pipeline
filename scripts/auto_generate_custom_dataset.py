import os
import json
import glob
from pathlib import Path
import sys
import re

# Add the current directory to the path so we can import render_settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def group_images_by_part_folder(image_files):
    """
    Group images by part folder (e.g., part_000/isometric.png, part_000/front.png -> same part)
    """
    part_groups = {}
    
    for img_file in image_files:
        # Get the folder name (part_000, part_001, etc.)
        folder_name = os.path.basename(os.path.dirname(img_file))
        
        # Check if it's a part folder (starts with "part_")
        if folder_name.startswith("part_"):
            if folder_name not in part_groups:
                part_groups[folder_name] = []
            part_groups[folder_name].append(img_file)
    
    return part_groups

def group_images_by_part_filename(image_files):
    """
    Group images by part number in filename (e.g., part_000_iso.png, part_000_front.png -> same part)
    """
    part_groups = {}
    
    for img_file in image_files:
        filename = os.path.basename(img_file)
        # Extract part number (e.g., "part_000" from "part_000_iso.png")
        match = re.match(r'(part_\d+)', filename)
        if match:
            part_id = match.group(1)
            if part_id not in part_groups:
                part_groups[part_id] = []
            part_groups[part_id].append(img_file)
    
    return part_groups

def auto_generate_custom_dataset(cleanup_after=False, multi_view=False):
    """
    Automatically generates custom_test_images.jsonl from all images in test100_images folder.
    Creates one entry per image with the same prompt template.
    
    Args:
        cleanup_after (bool): If True, deletes images after processing. If False, keeps images for pipeline.
        multi_view (bool): If True, groups images by part and creates multi-view entries.
    """
    

    
    # Define paths
    test_images_dir = "./inference/test100_images"
    output_file = "./inference/custom_test_images.jsonl"
    
    # Check if test_images directory exists
    if not os.path.exists(test_images_dir):
        print(f"Error: Directory {test_images_dir} does not exist!")
        return
    
    # Clear existing JSONL file first
    if os.path.exists(output_file):
        print(f"Clearing existing {output_file}...")
        os.remove(output_file)
    
    # Get all image files (common image extensions)
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff', '*.tif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(test_images_dir, "**", ext), recursive=True))
    
    # Remove duplicates (case-insensitive)
    unique_files = []
    seen_names = set()
    for img_file in image_files:
        img_name = os.path.basename(img_file).lower()
        if img_name not in seen_names:
            seen_names.add(img_name)
            unique_files.append(img_file)
    
    image_files = unique_files
    
    if not image_files:
        print(f"No image files found in {test_images_dir}")
        return
    
    # Sort files for consistent ordering
    image_files.sort()
    
    print(f"Found {len(image_files)} image files:")
    for img_file in image_files:
        print(f"  - {img_file}")
    
    # Generate JSONL entries
    entries = []
    
    if multi_view:
        # First try to group by folder structure (new PartPacker format)
        part_groups = group_images_by_part_folder(image_files)
        
        if part_groups:
            print(f"\nGrouped into {len(part_groups)} parts by folder structure:")
            
            for i, (part_id, part_images) in enumerate(part_groups.items(), start=1):
                # Sort images within each part
                part_images.sort()
                
                print(f"  {part_id}: {len(part_images)} views")
                for img_file in part_images:
                    print(f"    - {os.path.relpath(img_file, test_images_dir)}")
                
                # Create multi-view entry with relative paths
                entry = {
                    "question_id": f"custom_{i:03d}",  # custom_001, custom_002, etc.
                    "images": [os.path.relpath(img_file, test_images_dir) for img_file in part_images],  # Relative paths
                    "text": "Generate the CADQuery code needed to create the CAD for the provided image.\nJust the code, no other words.",
                    "category": "multi_view",
                    "ground_truth": ""
                }
                entries.append(entry)
        else:
            # Fallback to filename grouping (old format)
            part_groups = group_images_by_part_filename(image_files)
            print(f"\nGrouped into {len(part_groups)} parts by filename:")
            
            for i, (part_id, part_images) in enumerate(part_groups.items(), start=1):
                # Sort images within each part
                part_images.sort()
                
                print(f"  {part_id}: {len(part_images)} views")
                for img_file in part_images:
                    print(f"    - {os.path.basename(img_file)}")
                
                # Create multi-view entry
                entry = {
                    "question_id": f"custom_{i:03d}",  # custom_001, custom_002, etc.
                    "images": [os.path.basename(img_file) for img_file in part_images],  # Just filenames
                    "text": "Generate the CADQuery code needed to create the CAD for the provided image.\nJust the code, no other words.",
                    "category": "multi_view",
                    "ground_truth": ""
                }
                entries.append(entry)
    else:
        # Single view per entry (original behavior)
        for i, img_file in enumerate(image_files, start=1):
            # Get relative path from test_images_dir
            img_relative_path = os.path.relpath(img_file, test_images_dir)
            
            # Create entry
            entry = {
                "question_id": f"custom_{i:03d}",  # custom_001, custom_002, etc.
                "image": img_relative_path,  # Relative path
                "text": "Generate the CADQuery code needed to create the CAD for the provided image.\nJust the code, no other words.",
                "category": "default",
                "ground_truth": ""
            }
            entries.append(entry)
    
    # Write to JSONL file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"\nSuccessfully generated {output_file} with {len(entries)} entries:")
    for entry in entries:
        if multi_view:
            print(f"  - {entry['question_id']}: {len(entry['images'])} views")
        else:
            print(f"  - {entry['question_id']}: {entry['image']}")
    
    # Only clear the test100_images folder if cleanup_after is True
    if cleanup_after:
        print(f"\nClearing {test_images_dir} folder...")
        for img_file in image_files:
            try:
                os.remove(img_file)
                print(f"  - Deleted: {os.path.relpath(img_file, test_images_dir)}")
            except Exception as e:
                print(f"  - Error deleting {os.path.relpath(img_file, test_images_dir)}: {e}")
        
        # Also remove empty folders
        for root, dirs, files in os.walk(test_images_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # If folder is empty
                        os.rmdir(dir_path)
                        print(f"  - Removed empty folder: {os.path.relpath(dir_path, test_images_dir)}")
                except Exception as e:
                    print(f"  - Error removing folder {os.path.relpath(dir_path, test_images_dir)}: {e}")
        
        print(f"\n✅ Process complete! {len(image_files)} images processed and folder cleared.")
        print(f"📁 New images can now be added to {test_images_dir} for the next generation cycle.")
    else:
        print(f"\n✅ Process complete! {len(image_files)} images processed.")
        print(f"📁 Images kept in {test_images_dir} for CAD generation pipeline.")

def cleanup_images():
    """
    Cleanup function to delete images after the entire pipeline is completed.
    """
    test_images_dir = "./inference/test100_images"
    
    if not os.path.exists(test_images_dir):
        print(f"Directory {test_images_dir} does not exist!")
        return
    
    # Get all image files recursively
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff', '*.tif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(test_images_dir, "**", ext), recursive=True))
    
    if not image_files:
        print(f"No image files found in {test_images_dir}")
        return
    
    print(f"Cleaning up {len(image_files)} images from {test_images_dir}...")
    for img_file in image_files:
        try:
            os.remove(img_file)
            print(f"  - Deleted: {os.path.relpath(img_file, test_images_dir)}")
        except Exception as e:
            print(f"  - Error deleting {os.path.relpath(img_file, test_images_dir)}: {e}")
    
    # Also remove empty folders
    for root, dirs, files in os.walk(test_images_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # If folder is empty
                    os.rmdir(dir_path)
                    print(f"  - Removed empty folder: {os.path.relpath(dir_path, test_images_dir)}")
            except Exception as e:
                print(f"  - Error removing folder {os.path.relpath(dir_path, test_images_dir)}: {e}")
    
    print(f"✅ Cleanup complete! {len(image_files)} images deleted.")

if __name__ == "__main__":
    # Default behavior: don't cleanup (for pipeline use), single view
    auto_generate_custom_dataset(cleanup_after=False, multi_view=False)
