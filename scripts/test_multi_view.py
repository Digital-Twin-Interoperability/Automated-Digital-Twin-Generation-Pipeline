#!/usr/bin/env python3
"""
Test script for multi-view functionality.
This script demonstrates how to use the multi-view dataset generation.
"""

import os
import sys
from auto_generate_custom_dataset import auto_generate_custom_dataset

def test_multi_view():
    """Test the multi-view dataset generation."""
    
    print("🧪 Testing Multi-View Dataset Generation")
    print("=" * 50)
    
    # Test single view (original behavior)
    print("\n1️⃣ Testing Single View Mode:")
    auto_generate_custom_dataset(cleanup_after=False, multi_view=False)
    
    # Test multi view
    print("\n2️⃣ Testing Multi-View Mode:")
    auto_generate_custom_dataset(cleanup_after=False, multi_view=True)
    
    print("\n✅ Multi-view test completed!")
    print("\n📋 Usage Instructions:")
    print("  • Single view: python scripts/auto_generate_custom_dataset.py")
    print("  • Multi view:  python -c \"from scripts.auto_generate_custom_dataset import auto_generate_custom_dataset; auto_generate_custom_dataset(multi_view=True)\"")

if __name__ == "__main__":
    test_multi_view()






