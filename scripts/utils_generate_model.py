import json
import subprocess
import trimesh
from trimesh.sample import sample_surface
import numpy as np
from plyfile import PlyData, PlyElement
import os
import random
from scipy.spatial import cKDTree as KDTree
import ast

def read_jsonl(file_path, *keys):
    """
    Reads a JSONL file and extracts specific keys from each dictionary.

    Args:
        file_path (str): Path to the JSONL file.
        *keys (str): One or more keys to extract from each JSON object.

    Returns:
        tuple: A tuple of lists, each corresponding to the extracted values for a given key.
    """
    results = {key: [] for key in keys}  # Create a dictionary to store lists for each key

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)  # Parse each line as a JSON object
            for key in keys:
                results[key].append(data.get(key, None))  # Append value or None if key is missing

    return tuple(results[key] for key in keys)  # Return lists as a tuple


def write_python_file(file_content, py_path):
    with open(py_path, "w", encoding="utf-8") as file:
        file.write(file_content)
    return

def run_python_script(py_path):
    """Run Python script by importing and executing it instead of using subprocess"""
    try:
        # Read the Python file
        with open(py_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Create a new namespace for execution
        namespace = {}
        
        # Execute the code in the namespace
        exec(code, namespace)
        
        return True
    except ModuleNotFoundError as e:
        if "OCP" in str(e):
            print(f"Direct execution error for {py_path}: OpenCascade Python bindings (OCP) not available")
            print("  This is required for CadQuery to work. Please install OCP using:")
            print("  conda install -c conda-forge ocp")
            print("  or")
            print("  pip install OCP")
        else:
            print(f"Direct execution error for {py_path}: Missing module - {e}")
        return False
    except Exception as e:
        print(f"Direct execution error for {py_path}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
# Writing ply file, from GenCAD/Ferdous's repo
def write_ply(points, filename, text=False):
    """ input: Nx3, write points to filename as PLY format. """
    points = [(points[i,0], points[i,1], points[i,2]) for i in range(points.shape[0])]
    vertex = np.array(points, dtype=[('x', 'f4'), ('y', 'f4'),('z', 'f4')])
    el = PlyElement.describe(vertex, 'vertex', comments=['vertices'])
    with open(filename, mode='wb') as f:
        PlyData([el], text=text).write(f)
    return

# From DeepCAD
def convert_stl_to_point_cloud(stl_path, point_cloud_path, n_points, seed=42):
    np.random.seed(seed)
    out_mesh = trimesh.load(stl_path) # load the stl as a mesh
    out_pc, _ = sample_surface(out_mesh, n_points) # convert to a point cloud
    write_ply(out_pc, point_cloud_path)
    return out_pc

def validate_cadquery_syntax(code):
    """Validate CadQuery code syntax without importing the actual modules"""
    try:
        # Parse the Python code to check for syntax errors
        ast.parse(code)
        
        # Check for common CadQuery patterns
        required_patterns = [
            'import cadquery',
            'cq.Workplane',
            'cq.Plane',
            'cq.Vector'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in code:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"  Warning: Missing expected CadQuery patterns: {missing_patterns}")
            return False
        
        return True
    except SyntaxError as e:
        print(f"  Syntax error in code: {e}")
        return False
    except Exception as e:
        print(f"  Code validation error: {e}")
        return False