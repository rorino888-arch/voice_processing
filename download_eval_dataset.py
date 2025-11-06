#!/usr/bin/env python3
"""
Script to download the evaluation dataset from HuggingFace.
Downloads the flock-io/flock-off-s1-character-roleplay dataset used for evaluation.
"""

import os
import argparse
from dotenv import load_dotenv
from flockoff.validator.trainer import download_dataset
from flockoff.constants import Competition
import flockoff.constants as constants

load_dotenv()


def download_eval_dataset():
    """Download the evaluation dataset."""
    parser = argparse.ArgumentParser(description="Download FLock evaluation dataset")
    parser.add_argument(
        "--eval_data_dir",
        type=str,
        default="./data/eval_data",
        help="Directory to save the evaluation dataset"
    )
    parser.add_argument(
        "--cache_dir",
        type=str,
        default=None,
        help="Directory for HF cache (optional)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if already exists"
    )
    
    args = parser.parse_args()
    
    # Expand home directory paths
    if args.eval_data_dir and args.eval_data_dir.startswith("~"):
        args.eval_data_dir = os.path.expanduser(args.eval_data_dir)
    if args.cache_dir and args.cache_dir.startswith("~"):
        args.cache_dir = os.path.expanduser(args.cache_dir)
    
    print("=" * 80)
    print("DOWNLOADING EVALUATION DATASET")
    print("=" * 80)
    
    # Get competition info
    competition = Competition.from_defaults()
    eval_namespace = competition.repo
    eval_commit = constants.eval_commit
    
    print(f"\nDataset: {eval_namespace}")
    print(f"Commit: {eval_commit}")
    print(f"Target directory: {args.eval_data_dir}")
    print()
    
    # Download the dataset
    print("Starting download...")
    download_dataset(
        namespace=eval_namespace,
        revision=eval_commit,
        local_dir=args.eval_data_dir,
        cache_dir=args.cache_dir,
        force=args.force
    )
    
    # Ensure directory exists
    os.makedirs(args.eval_data_dir, exist_ok=True)
    
    # Rename any .jsonl file to data.jsonl (as validator does)
    for fname in os.listdir(args.eval_data_dir):
        if fname.endswith(".jsonl"):
            src = os.path.join(args.eval_data_dir, fname)
            dst = os.path.join(args.eval_data_dir, "data.jsonl")
            if src != dst:
                os.replace(src, dst)
                print(f"Renamed {fname} → data.jsonl")
    
    # Verify download
    data_file = os.path.join(args.eval_data_dir, "data.jsonl")
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            lines = len(f.readlines())
        print(f"\n✅ Successfully downloaded!")
        print(f"   File: {data_file}")
        print(f"   Entries: {lines}")
    else:
        print(f"\n❌ Download completed but data.jsonl not found in {args.eval_data_dir}")
        print(f"   Listing files in directory:")
        for fname in os.listdir(args.eval_data_dir):
            print(f"     - {fname}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    download_eval_dataset()

