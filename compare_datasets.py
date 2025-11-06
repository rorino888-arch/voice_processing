#!/usr/bin/env python3
"""
Compare all miner datasets using the validator's duplicate detection logic.
This script:
1. Checks each miner dataset against the evaluation dataset
2. Finds duplicate groups between miner datasets
3. Reports detailed statistics
"""

import os
import argparse
from pathlib import Path
from collections import defaultdict

# Import validator utilities
from flockoff.validator.validator_utils import load_jsonl, count_similar
from flockoff import constants


def compare_datasets(data_dir, eval_data_dir):
    """
    Compare all datasets using validator's duplicate detection logic.
    
    Args:
        data_dir: Directory containing miner_* subdirectories
        eval_data_dir: Directory containing evaluation dataset
    """
    data_path = Path(data_dir)
    eval_data_path = Path(eval_data_dir)
    
    if not data_path.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return
    
    if not eval_data_path.exists():
        print(f"Error: Directory {eval_data_dir} does not exist")
        return
    
    print("=" * 80)
    print("DATASET COMPARISON USING VALIDATOR LOGIC")
    print("=" * 80)
    print()
    
    # Load evaluation dataset
    eval_file = eval_data_path / "data.jsonl"
    if not eval_file.exists():
        print(f"Error: {eval_file} not found")
        return
    
    print(f"Loading evaluation dataset: {eval_file}")
    try:
        eval_data = load_jsonl(str(eval_file))
        print(f"Loaded {len(eval_data)} entries from evaluation dataset")
    except Exception as e:
        print(f"Error loading evaluation dataset: {e}")
        return
    
    print()
    
    # Find all miner directories
    miner_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith('miner_')])
    
    if not miner_dirs:
        print("No miner directories found")
        return
    
    print(f"Found {len(miner_dirs)} miner datasets to compare")
    print()
    
    # Load all miner datasets
    miner_datasets = {}
    for miner_dir in miner_dirs:
        data_file = miner_dir / "data.jsonl"
        if not data_file.exists():
            print(f"Skipping {miner_dir.name}: data.jsonl not found")
            continue
        
        try:
            # Load with max_rows like validator does
            miner_data = load_jsonl(str(data_file), max_rows=constants.Competition.from_defaults().rows)
            miner_datasets[miner_dir.name] = miner_data
            print(f"Loaded {miner_dir.name}: {len(miner_data)} entries")
        except Exception as e:
            print(f"Error loading {miner_dir.name}: {e}")
            continue
    
    print()
    print("=" * 80)
    
    # Check 1: Each miner vs evaluation dataset
    print("\nCHECK 1: Mining vs Evaluation Dataset")
    print("=" * 80)
    print("\nChecking if each miner dataset is entirely from evaluation dataset...")
    
    eval_violations = []
    for miner_name, miner_data in miner_datasets.items():
        similar_count = count_similar(eval_data, miner_data)
        total_miner = len(miner_data)
        
        if similar_count != total_miner:
            eval_violations.append(miner_name)
            print(f"❌ {miner_name}: {similar_count}/{total_miner} entries match eval dataset (INVALID)")
        else:
            print(f"✅ {miner_name}: {similar_count}/{total_miner} entries match eval dataset")
    
    if eval_violations:
        print(f"\n⚠️  {len(eval_violations)} miner(s) violated evaluation dataset constraint:")
        for violator in eval_violations:
            print(f"   - {violator}")
    
    print()
    
    # Check 2: Find duplicate groups between miners
    print("CHECK 2: Duplicate Detection Between Miners")
    print("=" * 80)
    print("\nComparing miner datasets against each other...")
    print(f"Using duplicate threshold: {constants.DEFAULT_DUPLICATE_COUNT} similar entries")
    print()
    
    # Track which miners have been processed
    processed = set()
    duplicate_groups = []
    similarity_matrix = {}
    
    # Compare all pairs
    for miner_i in miner_datasets.keys():
        if miner_i in processed:
            continue
        
        similar_miners = [miner_i]
        
        for miner_j in miner_datasets.keys():
            if miner_i == miner_j or miner_j in processed:
                continue
            
            # Count similar entries
            similar_count = count_similar(miner_datasets[miner_i], miner_datasets[miner_j])
            
            # Store for matrix
            similarity_matrix[(miner_i, miner_j)] = similar_count
            
            # Check if exceeds threshold
            if similar_count > constants.DEFAULT_DUPLICATE_COUNT:
                similar_miners.append(miner_j)
                print(f"🔍 Found duplicates: {miner_i} ↔ {miner_j} ({similar_count} similar entries)")
        
        # If we found a group, mark them all as processed
        if len(similar_miners) > 1:
            duplicate_groups.append(similar_miners)
            processed.update(similar_miners)
        else:
            processed.add(miner_i)
    
    print()
    
    # Report duplicate groups
    if duplicate_groups:
        print("📊 DUPLICATE GROUPS FOUND:")
        for i, group in enumerate(duplicate_groups, 1):
            print(f"\nGroup {i}: {len(group)} miner(s)")
            for miner in group:
                print(f"   - {miner}")
    else:
        print("✅ No duplicate groups found (all datasets are unique)")
    
    # Calculate similarity percentages
    print()
    print("CHECK 3: Similarity Statistics")
    print("=" * 80)
    print("\nDetailed similarity matrix:")
    
    # Find maximum similarity for alignment
    max_sim = max(similarity_matrix.values()) if similarity_matrix else 0
    width = max(len(str(max_sim)), 8)
    
    # Print similarity matrix
    print(f"\n{'':15}", end="")
    for miner_j in sorted(miner_datasets.keys()):
        print(f"{miner_j:>15}", end="")
    print()
    
    for miner_i in sorted(miner_datasets.keys()):
        print(f"{miner_i:15}", end="")
        for miner_j in sorted(miner_datasets.keys()):
            if miner_i == miner_j:
                print(f"{'—':>15}", end="")
            else:
                sim = similarity_matrix.get((miner_i, miner_j), 0)
                # Calculate percentage
                pct = (sim / len(miner_datasets[miner_i]) * 100) if miner_datasets[miner_i] else 0
                print(f"{sim:>15}", end="")
        print()
    
    # Summary statistics
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_miners = len(miner_datasets)
    unique_miners = total_miners - sum(len(g) - 1 for g in duplicate_groups)
    dup_miners = sum(len(g) - 1 for g in duplicate_groups)
    
    print(f"\nTotal miners analyzed: {total_miners}")
    print(f"Unique datasets: {unique_miners}")
    print(f"Duplicated miners: {dup_miners}")
    print(f"Duplicate groups: {len(duplicate_groups)}")
    print(f"Evaluation dataset violations: {len(eval_violations)}")
    
    # Calculate average similarity
    if similarity_matrix:
        avg_sim = sum(similarity_matrix.values()) / len(similarity_matrix)
        print(f"\nAverage similarity between datasets: {avg_sim:.1f} entries")
        print(f"Maximum similarity: {max_sim} entries")
    
    print()
    print("=" * 80)
    
    # Detailed per-miner stats
    print("\nPer-Miner Statistics:")
    print("=" * 80)
    for miner_name in sorted(miner_datasets.keys()):
        data = miner_datasets[miner_name]
        print(f"\n{miner_name}:")
        print(f"  Total entries: {len(data)}")
        
        # Count similarities with all other miners
        similarities = [(j, similarity_matrix.get((miner_name, j), 0)) 
                       for j in miner_datasets.keys() if j != miner_name]
        if similarities:
            max_match = max(similarities, key=lambda x: x[1])
            pct = (max_match[1] / len(data) * 100) if data else 0
            print(f"  Max overlap: {max_match[1]} entries with {max_match[0]} ({pct:.1f}%)")
        
        # Check if in a duplicate group
        in_group = any(miner_name in g for g in duplicate_groups)
        print(f"  Status: {'❌ In duplicate group' if in_group else '✅ Unique'}")
    
    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Compare datasets using validator logic")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./data/miner_datasets",
        help="Directory containing miner_* subdirectories"
    )
    parser.add_argument(
        "--eval_data_dir",
        type=str,
        default="./data/eval_data",
        help="Directory containing evaluation dataset"
    )
    
    args = parser.parse_args()
    
    # Expand home directory paths
    if args.data_dir.startswith("~"):
        args.data_dir = os.path.expanduser(args.data_dir)
    if args.eval_data_dir.startswith("~"):
        args.eval_data_dir = os.path.expanduser(args.eval_data_dir)
    
    compare_datasets(args.data_dir, args.eval_data_dir)


if __name__ == "__main__":
    main()

