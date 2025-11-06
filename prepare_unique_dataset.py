#!/usr/bin/env python3
"""
Script to prepare a unique dataset for mining.
Selects 250 entries from eval_data that are NOT in any existing miner dataset.
Ensures your miner dataset will be unique and avoid penalties.
"""

import json
import os
import argparse
import random
from pathlib import Path
from typing import Set, List


def load_jsonl(path, max_rows=None):
    """Load JSONL file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = [json.loads(line.strip()) for line in f if line.strip()]
        if max_rows is not None:
            data = data[:max_rows]
        return data


def jsonl_to_set(jsonl_data):
    """Convert JSONL data to a set of JSON strings (for comparison)."""
    return set(json.dumps(item, sort_keys=True) for item in jsonl_data)


def load_miner_datasets(data_dir):
    """Load all miner datasets as a list of lists."""
    print("\nLoading all miner datasets...")
    
    data_path = Path(data_dir)
    miner_datasets = []
    
    if not data_path.exists():
        print(f"Warning: Directory {data_dir} does not exist")
        return miner_datasets
    
    miner_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith('miner_')])
    
    for miner_dir in miner_dirs:
        data_file = miner_dir / "data.jsonl"
        if data_file.exists():
            try:
                miner_data = load_jsonl(data_file)
                miner_datasets.append((miner_dir.name, miner_data))
            except Exception as e:
                print(f"Warning: Could not read {data_file}: {e}")
    
    print(f"Loaded {len(miner_datasets)} miner datasets")
    return miner_datasets


def count_similar(jsonl1, jsonl2):
    """Count similar entries between two JSONL datasets (same as validator)."""
    set1 = set(json.dumps(item, sort_keys=True) for item in jsonl1)
    set2 = set(json.dumps(item, sort_keys=True) for item in jsonl2)
    return len(set1 & set2)


def find_unique_entries(eval_data, miner_datasets, num_needed=250, duplicate_threshold=100):
    """
    Find unique entries from eval_data that will have <=100 overlap with any miner.
    Uses efficient algorithm: collect all used entries, then select from unused.
    
    Args:
        eval_data: List of eval dataset entries
        miner_datasets: List of (miner_name, dataset_list) tuples
        num_needed: Number of unique entries needed
        duplicate_threshold: Maximum overlap allowed (default: 100, same as validator)
    
    Returns:
        List of unique entries
    """
    print(f"Finding entries that have <= {duplicate_threshold} overlap with any miner...")
    
    # Phase 1: Collect all entries used by miners (optimized)
    print("  Phase 1: Building index of all used entries...")
    all_used_entries = set()
    for miner_name, miner_data in miner_datasets:
        miner_entries_set = jsonl_to_set(miner_data)
        all_used_entries.update(miner_entries_set)
    
    print(f"  Found {len(all_used_entries)} unique entries used by miners")
    
    # Phase 2: Find completely unused entries
    print("  Phase 2: Finding completely unused entries...")
    eval_entries_set = jsonl_to_set(eval_data)
    completely_unused = []
    
    for entry in eval_data:
        entry_str = json.dumps(entry, sort_keys=True)
        if entry_str not in all_used_entries:
            completely_unused.append(entry)
    
    print(f"  Found {len(completely_unused)} entries not used by ANY miner")
    
    # Phase 3: Select random sample from completely unused entries
    if len(completely_unused) >= num_needed:
        print(f"  Phase 3: Randomly selecting {num_needed} from unused entries...")
        selected = random.sample(completely_unused, num_needed)
        print(f"✅ Successfully found {len(selected)} completely unique entries")
    else:
        print(f"⚠️  Only {len(completely_unused)} completely unused entries available")
        print(f"  Will need to use entries with some overlap...")
        # Fallback: use what we have
        selected = completely_unused
        if len(selected) < num_needed:
            # Additional fallback: try adding entries one by one and check overlap
            remaining_needed = num_needed - len(selected)
            print(f"  Trying to find {remaining_needed} more entries with minimal overlap...")
            
            # Get entries that might have minimal overlap
            remaining_candidates = [e for e in eval_data if e not in completely_unused]
            
            for candidate in remaining_candidates[:remaining_needed * 10]:  # Try up to 10x candidates
                test_set = selected + [candidate]
                max_overlap = 0
                for miner_name, miner_data in miner_datasets:
                    overlap = count_similar(test_set, miner_data)
                    if overlap > max_overlap:
                        max_overlap = overlap
                
                if max_overlap <= duplicate_threshold:
                    selected.append(candidate)
                    if len(selected) >= num_needed:
                        break
    
    print(f"Final result: {len(selected)} unique entries")
    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a unique dataset for mining by selecting entries not in other miners' datasets"
    )
    parser.add_argument(
        "--eval_data_file",
        type=str,
        default="./data/eval_data/data.jsonl",
        help="Path to evaluation dataset"
    )
    parser.add_argument(
        "--miner_data_dir",
        type=str,
        default="./data",
        help="Directory containing miner_* subdirectories"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="./data/1/data.jsonl",
        help="Output file for your unique dataset"
    )
    parser.add_argument(
        "--num_entries",
        type=int,
        default=250,
        help="Number of entries to select (default: 250)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: random)"
    )
    
    args = parser.parse_args()
    
    # Expand home directory paths
    if args.eval_data_file.startswith("~"):
        args.eval_data_file = os.path.expanduser(args.eval_data_file)
    if args.miner_data_dir.startswith("~"):
        args.miner_data_dir = os.path.expanduser(args.miner_data_dir)
    if args.output_file.startswith("~"):
        args.output_file = os.path.expanduser(args.output_file)
    
    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)
    
    print("=" * 100)
    print("PREPARING UNIQUE DATASET FOR MINING")
    print("=" * 100)
    
    # Load eval dataset
    print(f"\nLoading evaluation dataset: {args.eval_data_file}")
    if not Path(args.eval_data_file).exists():
        print(f"ERROR: Evaluation dataset not found at {args.eval_data_file}")
        return
    
    eval_data = load_jsonl(args.eval_data_file)
    print(f"Loaded {len(eval_data)} entries from evaluation dataset")
    
    # Load all miner datasets
    miner_datasets = load_miner_datasets(args.miner_data_dir)
    
    # Find unique entries (compares with each miner individually)
    print(f"\nFinding {args.num_entries} unique entries...")
    unique_entries = find_unique_entries(eval_data, miner_datasets, args.num_entries)
    
    if len(unique_entries) < args.num_entries:
        print(f"\n❌ ERROR: Cannot create unique dataset with {args.num_entries} entries")
        print(f"   Only {len(unique_entries)} unique entries available")
        print(f"   You need to reduce --num_entries or wait for more eval data")
        return
    
    # Sort entries alphabetically (for consistency)
    print("Sorting entries alphabetically...")
    unique_entries_sorted = sorted(unique_entries, key=lambda x: json.dumps(x, sort_keys=True))
    
    # Write to output file
    print(f"\nWriting {len(unique_entries_sorted)} entries to: {args.output_file}")
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        for entry in unique_entries_sorted:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    # Verify uniqueness against each miner individually
    print("\nVerifying uniqueness against each miner...")
    max_overlap = 0
    max_overlap_miner = None
    
    for miner_name, miner_data in miner_datasets:
        overlap = count_similar(unique_entries_sorted, miner_data)
        if overlap > max_overlap:
            max_overlap = overlap
            max_overlap_miner = miner_name
    
    print(f"Maximum overlap with any miner: {max_overlap} entries ({max_overlap/len(unique_entries_sorted)*100:.1f}%)")
    if max_overlap_miner:
        print(f"  Most similar miner: {max_overlap_miner}")
    
    # Check if passes threshold
    duplicate_threshold = 100
    if max_overlap <= duplicate_threshold:
        print(f"✅ SUCCESS: Dataset passes validator checks (<= {duplicate_threshold} overlap)")
    else:
        print(f"❌ WARNING: Dataset exceeds threshold (>{duplicate_threshold} overlap with {max_overlap_miner})")
    
    # Print summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"✅ Created unique dataset: {args.output_file}")
    print(f"   Total entries: {len(unique_entries_sorted)}")
    print(f"   Max overlap with any miner: {max_overlap} entries ({max_overlap/len(unique_entries_sorted)*100:.1f}%)")
    print(f"   Most similar miner: {max_overlap_miner if max_overlap_miner else 'None'}")
    print(f"   Random seed: {args.seed if args.seed else 'random'}")
    print("\n📝 Next steps:")
    print(f"   1. Review your dataset: cat {args.output_file} | head -5")
    print(f"   2. Check it's unique: python3 check_datasets.py --data_dir {args.miner_data_dir}")
    print(f"   3. Upload to HuggingFace and register with miner")
    print("=" * 100)


if __name__ == "__main__":
    main()

