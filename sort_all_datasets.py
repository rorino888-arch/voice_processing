#!/usr/bin/env python3
"""
Script to sort all miner dataset files alphabetically by their JSON content.
This reads each data.jsonl file, sorts the lines alphabetically, and writes them back.
"""

import os
import json
import argparse
from pathlib import Path


def sort_dataset_file(file_path):
    """
    Sort a JSONL file alphabetically by its JSON content.
    
    Args:
        file_path: Path to the data.jsonl file
    """
    print(f"Sorting: {file_path}")
    
    try:
        # Read all lines
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip if empty
        if not lines:
            print(f"  → Empty file, skipping")
            return False
        
        # Parse JSON lines
        data = []
        for line in lines:
            if line.strip():
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"  → Error parsing line: {e}")
                    return False
        
        # Sort alphabetically by JSON string representation
        # This ensures consistent ordering across different keys
        data_sorted = sorted(data, key=lambda x: json.dumps(x, sort_keys=True))
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data_sorted:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"  → Sorted {len(data_sorted)} entries")
        return True
        
    except Exception as e:
        print(f"  → Error: {e}")
        return False


def sort_all_datasets(data_dir):
    """
    Sort all dataset files in the directory.
    
    Args:
        data_dir: Directory containing miner_* subdirectories
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return
    
    print(f"Scanning directory: {data_dir}")
    print("=" * 80)
    
    # Find all miner directories
    miner_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith('miner_')])
    
    if not miner_dirs:
        print("No miner directories found")
        return
    
    print(f"Found {len(miner_dirs)} miner directories\n")
    
    # Process each miner directory
    successful = 0
    failed = 0
    skipped = 0
    
    for miner_dir in miner_dirs:
        data_file = miner_dir / "data.jsonl"
        
        if not data_file.exists():
            print(f"Skipping {miner_dir.name}: data.jsonl not found")
            skipped += 1
            continue
        
        # Sort the file
        if sort_dataset_file(data_file):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SORTING SUMMARY")
    print("=" * 80)
    print(f"Total miner directories: {len(miner_dirs)}")
    print(f"Successfully sorted: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped (no file): {skipped}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Sort all miner dataset files alphabetically")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./data",
        help="Directory containing miner_* subdirectories with data.jsonl files"
    )
    
    args = parser.parse_args()
    
    # Expand home directory
    if args.data_dir.startswith("~"):
        args.data_dir = os.path.expanduser(args.data_dir)
    
    sort_all_datasets(args.data_dir)


if __name__ == "__main__":
    main()

