#!/usr/bin/env python3
"""
Script to check if miner datasets are from the evaluation dataset.
Uses the validator's duplicate detection logic to identify datasets that copy from eval_data.
"""

import json
import os
import argparse
from pathlib import Path


def load_jsonl(path, max_rows=None):
    """Load JSONL file (same as validator)."""
    with open(path, 'r', encoding='utf-8') as f:
        data = [json.loads(line.strip()) for line in f if line.strip()]
        if max_rows is not None:
            data = data[:max_rows]
        return data


def count_similar(jsonl1, jsonl2):
    """
    Count similar entries between two JSONL datasets (same as validator).
    Returns the number of entries that appear in both datasets.
    """
    set1 = set(json.dumps(item, sort_keys=True) for item in jsonl1)
    set2 = set(json.dumps(item, sort_keys=True) for item in jsonl2)
    return len(set1 & set2)


def check_miner_vs_eval(miner_file, eval_data, duplicate_threshold=100):
    """
    Check if a miner dataset matches the evaluation dataset.
    Returns a dict with match statistics.
    """
    try:
        miner_data = load_jsonl(miner_file)
        eval_data_subset = eval_data[:len(miner_data)] if len(miner_data) <= len(eval_data) else eval_data
        
        # Count matching entries
        similar_count = count_similar(miner_data, eval_data)
        total_miner = len(miner_data)
        total_eval = len(eval_data)
        
        # Calculate percentage
        match_pct = (similar_count / total_miner * 100) if total_miner > 0 else 0
        
        # Determine status
        is_duplicate = similar_count == total_miner
        is_majority_duplicate = similar_count >= duplicate_threshold
        is_suspicious = match_pct >= 50  # 50% or more matching
        
        return {
            "total_miner_entries": total_miner,
            "similar_entries": similar_count,
            "match_percentage": match_pct,
            "is_complete_duplicate": is_duplicate,
            "is_majority_duplicate": is_majority_duplicate,
            "is_suspicious": is_suspicious,
            "status": determine_status(similar_count, total_miner, is_duplicate, is_majority_duplicate)
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "ERROR"
        }


def determine_status(similar_count, total_miner, is_duplicate, is_majority_duplicate):
    """Determine human-readable status."""
    if total_miner == 0:
        return "EMPTY"
    if is_duplicate:
        return "⚠️  COMPLETE DUPLICATE"
    if is_majority_duplicate:
        return "⚠️  MAJOR DUPLICATE (>100 entries)"
    if similar_count >= 50:
        return "⚠️  HIGH SIMILARITY"
    if similar_count > 0:
        return "✓ SOME OVERLAP"
    return "✓ NO OVERLAP"


def check_all_datasets(data_dir, eval_data_file=None):
    """
    Check all miner datasets against the evaluation dataset.
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return
    
    # Load eval dataset
    if eval_data_file is None:
        # Try to find eval_data in the same directory structure
        eval_candidates = [
            data_path.parent / "eval_data" / "data.jsonl",
            Path("./data/eval_data/data.jsonl"),
            Path("../data/eval_data/data.jsonl"),
        ]
        
        for candidate in eval_candidates:
            if candidate.exists():
                eval_data_file = candidate
                break
    
    if eval_data_file is None or not Path(eval_data_file).exists():
        print(f"Error: Evaluation dataset not found. Expected at: {eval_data_file}")
        print("Please specify --eval_data_file")
        return
    
    print(f"Loading evaluation dataset: {eval_data_file}")
    eval_data = load_jsonl(eval_data_file)
    print(f"Evaluation dataset has {len(eval_data)} entries\n")
    
    # Find all miner directories
    miner_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith('miner_')])
    
    if not miner_dirs:
        print("No miner directories found")
        return
    
    print("=" * 100)
    print("CHECKING MINER DATASETS AGAINST EVALUATION DATASET")
    print("=" * 100)
    print()
    
    results = []
    
    for miner_dir in miner_dirs:
        data_file = miner_dir / "data.jsonl"
        miner_id = miner_dir.name
        
        if not data_file.exists():
            print(f"{miner_id:20} → SKIPPED (no data.jsonl)")
            continue
        
        # Check this miner's dataset
        result = check_miner_vs_eval(data_file, eval_data)
        result["miner_id"] = miner_id
        
        print(f"{miner_id:20} → ", end="")
        print(f"{result['status']:30}", end="")
        if "error" not in result:
            print(f" | {result['similar_entries']:3}/{result['total_miner_entries']:3} entries ({result['match_percentage']:5.1f}%)")
        else:
            print(f" | ERROR: {result['error']}")
        
        results.append(result)
    
    # Summary
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    complete_duplicates = sum(1 for r in results if r.get('is_complete_duplicate'))
    majority_duplicates = sum(1 for r in results if r.get('is_majority_duplicate'))
    suspicious = sum(1 for r in results if r.get('is_suspicious'))
    no_overlap = sum(1 for r in results if r.get('similar_entries', 0) == 0)
    
    print(f"Total miners checked: {len(results)}")
    print(f"Complete duplicates:  {complete_duplicates} ⚠️")
    print(f"Major duplicates:     {majority_duplicates} ⚠️")
    print(f"Suspicious (>50%):    {suspicious} ⚠️")
    print(f"No overlap:           {no_overlap} ✓")
    print("=" * 100)
    
    # Detailed report for duplicates
    if complete_duplicates > 0:
        print()
        print("⚠️  COMPLETE DUPLICATES (Copy entire eval dataset):")
        for r in results:
            if r.get('is_complete_duplicate'):
                print(f"   - {r['miner_id']}: {r['similar_entries']} entries identical")
    
    if majority_duplicates > 0 and complete_duplicates != majority_duplicates:
        print()
        print("⚠️  MAJOR DUPLICATES (>100 matching entries):")
        for r in results:
            if r.get('is_majority_duplicate') and not r.get('is_complete_duplicate'):
                print(f"   - {r['miner_id']}: {r['similar_entries']}/{r['total_miner_entries']} entries ({r['match_percentage']:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Check if miner datasets copy from eval dataset")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="./data",
        help="Directory containing miner_* subdirectories"
    )
    parser.add_argument(
        "--eval_data_file",
        type=str,
        default=None,
        help="Path to evaluation dataset data.jsonl"
    )
    
    args = parser.parse_args()
    
    # Expand home directory
    if args.data_dir.startswith("~"):
        args.data_dir = os.path.expanduser(args.data_dir)
    if args.eval_data_file and args.eval_data_file.startswith("~"):
        args.eval_data_file = os.path.expanduser(args.eval_data_file)
    
    check_all_datasets(args.data_dir, args.eval_data_file)


if __name__ == "__main__":
    main()

