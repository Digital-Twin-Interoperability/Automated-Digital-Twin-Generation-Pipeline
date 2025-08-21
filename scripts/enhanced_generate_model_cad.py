#!/usr/bin/env python3
"""
Enhanced CAD Model Generator with Multi-View Image Generation Toggle
Integrates with MultiViewManager for configurable image generation.
"""

import argparse
from utils_generate_model import *
import os
import pandas as pd
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time
import re

# Import multi-view manager
from multi_view_manager import MultiViewManager
from config import MultiViewConfig, get_preset_config

ROOT_CHECKPOINT_DIR = "./inference/inference_results"

def wait_for_file(file_path, timeout=2, check_interval=0.1):
    """Waits for a file to exist for a limited time."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.isfile(file_path):
            return True
        time.sleep(check_interval)
    return False

def process_cad_with_images(args_tuple):
    """Function to write and run a single Python script with optional image generation."""
    code, id_, code_dir, stl_dir, step_dir, pc_dir_base, pc_reps, code_language, multi_view_config = args_tuple
    
    print(f"Processing {id_}...")
    
    if "```python" in code:
        code = re.sub(r"```[a-zA-Z]*\n|```", "", code)

    # Check if the code can be run
    file_path = f"{code_dir}/{id_}.py"
    write_python_file(code, file_path)
    print(f"  Testing basic code execution for {id_}...")
    valid_code = run_python_script(file_path)
    print(f"  Basic code execution result for {id_}: {valid_code}")
    
    valid_stl = False
    valid_pc = False
    valid_images = False
    
    if valid_code:
        print(f"  Adding export code for {id_}...")
        
        # Add export code based on language
        if code_language == "pythonocc":
            code += f"\nwrite_stl_file(body, \"{stl_dir}/{id_}.stl\")"
            raise ValueError("Implement STEP generation")
        elif code_language == "cadquery":
            code += f"\nimport cadquery as cq\ncq.exporters.export(solid, \"{stl_dir}/{id_}.stl\")\n"
            code += f"\nimport cadquery as cq\ncq.exporters.export(solid, \"{step_dir}/{id_}.step\")\n"
        else:
            raise TypeError("CAD code language not supported!")
        
        write_python_file(code, f"{code_dir}/{id_}.py")
        print(f"  Testing STL generation for {id_}...")
        valid_stl = run_python_script(f"{code_dir}/{id_}.py")
        print(f"  STL generation result for {id_}: {valid_stl}")
        
        if not wait_for_file(f"{stl_dir}/{id_}.stl"):
            valid_stl = False
            print(f"  STL file not found for {id_}")
        
        # Generate point clouds if enabled
        if valid_stl and pc_reps > 0:
            print(f"  Generating point clouds for {id_}...")
            for i in range(pc_reps):
                try:
                    out_pc = convert_stl_to_point_cloud(f"{stl_dir}/{id_}.stl", f"{pc_dir_base}_{i}/{id_}.ply", 2000, seed=42+i)
                    if os.path.isfile(f"{pc_dir_base}_{i}/{id_}.ply"):
                        valid_pc = True
                except Exception as e:
                    print(f"{id_} failed point cloud generation: {e}")
        
        # Generate images if multi-view is enabled
        if valid_stl and multi_view_config and multi_view_config.enable_multi_view:
            print(f"  Generating images for {id_}...")
            try:
                valid_images = generate_images_for_part(id_, step_dir, multi_view_config)
                print(f"  Image generation result for {id_}: {valid_images}")
            except Exception as e:
                print(f"{id_} failed image generation: {e}")
                valid_images = False

    print(f"Completed processing {id_}: code={valid_code}, stl={valid_stl}, pc={valid_pc}, images={valid_images}")
    return valid_code, valid_stl, valid_pc, valid_images, id_

def generate_images_for_part(part_id, step_dir, config):
    """Generate images for a specific part using the multi-view manager."""
    step_file = os.path.join(step_dir, f"{part_id}.step")
    
    if not os.path.exists(step_file):
        print(f"  STEP file not found: {step_file}")
        return False
    
    try:
        # Initialize multi-view manager
        manager = MultiViewManager(config)
        
        # Process the single STEP file
        processed_files = manager.process_renderer_images(step_dir)
        
        # Check if images were generated for this part
        part_images = [f for f in processed_files if part_id in f]
        
        return len(part_images) > 0
        
    except Exception as e:
        print(f"  Error generating images for {part_id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Enhanced CAD Model Generator with Multi-View Image Generation")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of split/test dataset.")
    parser.add_argument("--model_tested", type=str, required=True, help="Name of model.")
    parser.add_argument("--code_language", type=str, required=True, help="Name of code language, cadquery or pythonocc are currently supported")
    parser.add_argument("--pc_reps", type=int, required=True, help="Number of reps of point cloud generation.")
    parser.add_argument("--parallel", action="store_true", help="Run in parallel using multiple CPUs.")
    
    # Multi-view configuration options
    parser.add_argument("--multi-view-config", type=str, help="Path to multi-view configuration file")
    parser.add_argument("--multi-view-preset", type=str, 
                       choices=['minimal', 'standard', 'full', 'partpacker_only', 'renderer_only'],
                       help="Use preset multi-view configuration")
    parser.add_argument("--enable-multi-view", action="store_true", help="Enable multi-view image generation")
    parser.add_argument("--enable-partpacker", action="store_true", help="Enable PartPacker integration")
    parser.add_argument("--enable-renderer", action="store_true", help="Enable renderer integration")
    parser.add_argument("--views", nargs='+', help="Views to generate (isometric, top, side, front, bottom)")
    parser.add_argument("--renderer-style", type=str, 
                       choices=['technical', 'blueprint', 'modern'],
                       help="Renderer style for CAD drawings")
    parser.add_argument("--composite-layout", type=str,
                       choices=['grid', 'horizontal', 'vertical'],
                       help="Composite image layout")

    args = parser.parse_args()
    
    # Load multi-view configuration
    multi_view_config = None
    if args.multi_view_config:
        from config import load_config
        multi_view_config = load_config(args.multi_view_config)
    elif args.multi_view_preset:
        multi_view_config = get_preset_config(args.multi_view_preset)
    elif args.enable_multi_view or args.enable_partpacker or args.enable_renderer:
        # Create custom configuration from command line arguments
        multi_view_config = MultiViewConfig(
            enable_multi_view=args.enable_multi_view,
            enable_partpacker=args.enable_partpacker,
            enable_renderer=args.enable_renderer
        )
        
        if args.views:
            multi_view_config.views = args.views
        
        if args.renderer_style:
            multi_view_config.renderer_style = args.renderer_style
        
        if args.composite_layout:
            multi_view_config.composite_layout = args.composite_layout
    
    # Print configuration summary
    if multi_view_config:
        from config import print_config_summary
        print("🔧 Multi-View Configuration:")
        print_config_summary(multi_view_config)
    
    model_name = args.model_tested.split("/")[-1]
    print(f"Model name: {model_name}")
    
    # Read model outputs
    model_code, ids, q_token_count, gt_token_count, output_token_count = read_jsonl(
        ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/merge.jsonl", 
        "text", "question_id", "question_token_count", "ground_truth_token_count", "output_token_count"
    )
    
    # Set up directories
    code_dir = ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/model_code"
    os.makedirs(code_dir, exist_ok=True)
    
    stl_dir = ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/model_stl"
    os.makedirs(stl_dir, exist_ok=True)
    
    step_dir = ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/model_step"
    os.makedirs(step_dir, exist_ok=True)
    
    pc_dir_base = ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/model_point_cloud"
    for i in range(args.pc_reps):
        os.makedirs(pc_dir_base + f"_{i}", exist_ok=True)
    
    # Prepare input data
    input_data = [
        (model_code[i], ids[i], code_dir, stl_dir, step_dir, pc_dir_base, 
         args.pc_reps, args.code_language, multi_view_config) 
        for i in range(len(model_code))
    ]
    
    if args.parallel:
        num_workers = min(8, cpu_count())
        with Pool(num_workers) as pool:
            cad_results = list(tqdm(
                pool.imap_unordered(process_cad_with_images, input_data), 
                total=len(input_data), 
                desc="Processing CAD tasks with images"
            ))
        
        valid_codes, valid_stls, valid_pcs, valid_images, ids_out = zip(*cad_results)
    else:
        raise ValueError("Only implemented with parallelization at this time")
    
    # Store results
    df = pd.DataFrame({
        "q_ids": list(ids_out), 
        "model_valid_code": list(valid_codes), 
        "model_valid_stl": list(valid_stls), 
        "model_valid_point_clouds": list(valid_pcs),
        "model_valid_images": list(valid_images)
    })
    
    # Calculate statistics
    code_valid_rate = df["model_valid_code"].sum() / len(df)
    stl_valid_rate = df["model_valid_stl"].sum() / len(df)
    pc_valid_rate = df["model_valid_point_clouds"].sum() / len(df)
    image_valid_rate = df["model_valid_images"].sum() / len(df) if "model_valid_images" in df.columns else 0
    
    # Write stats to file
    with open(ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/cad_gen_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Valid code: {code_valid_rate}\n")
        f.write(f"Valid stl: {stl_valid_rate}\n")
        f.write(f"Valid point cloud: {pc_valid_rate}\n")
        if multi_view_config and multi_view_config.enable_multi_view:
            f.write(f"Valid images: {image_valid_rate}\n")
    
    df.to_csv(ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}/results.csv")
    
    # Post-process with multi-view manager if enabled
    if multi_view_config and multi_view_config.enable_multi_view:
        print("\n🔄 Post-processing with Multi-View Manager...")
        try:
            manager = MultiViewManager(multi_view_config)
            manager.process_cadcoder_output(ROOT_CHECKPOINT_DIR + f"/{model_name}/{args.dataset_name}")
        except Exception as e:
            print(f"❌ Error in post-processing: {e}")
    
    print(f"\n✅ Processing complete!")
    print(f"📊 Results:")
    print(f"  - Valid code: {code_valid_rate:.2%}")
    print(f"  - Valid STL: {stl_valid_rate:.2%}")
    print(f"  - Valid point clouds: {pc_valid_rate:.2%}")
    if multi_view_config and multi_view_config.enable_multi_view:
        print(f"  - Valid images: {image_valid_rate:.2%}")

if __name__ == "__main__":
    main()



