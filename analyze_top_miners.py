#!/usr/bin/env python3
"""
Analyze top miners' datasets to understand what makes them successful.
"""

import json
import os
import hashlib
from collections import Counter

def load_jsonl(path):
    data = []
    with open(path, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                pass
    return data

def get_dataset_hash(data):
    sorted_entries = sorted([json.dumps(item, sort_keys=True) for item in data])
    combined = ''.join(sorted_entries)
    return hashlib.md5(combined.encode()).hexdigest()

def find_entry_positions(miner_data, eval_data):
    """Find where miner entries appear in eval dataset."""
    eval_set_to_idx = {}
    for i, entry in enumerate(eval_data):
        entry_str = json.dumps(entry, sort_keys=True)
        if entry_str not in eval_set_to_idx:
            eval_set_to_idx[entry_str] = i
    
    indices = []
    for entry in miner_data:
        entry_str = json.dumps(entry, sort_keys=True)
        if entry_str in eval_set_to_idx:
            indices.append(eval_set_to_idx[entry_str])
    return sorted(indices)

# Load eval dataset
print("Loading eval dataset...")
eval_data = load_jsonl("data/eval_data/data.jsonl")
print(f"Eval dataset: {len(eval_data)} entries")

# Top miner UIDs (from coldkey)
top_miner_uids = [1, 3, 7, 13, 14, 15, 16, 18, 20, 22, 23, 25, 28, 31, 32, 35, 36, 40, 45, 46, 48, 49, 52, 53, 55, 57, 58, 63, 64, 65, 68, 73, 79, 82, 83, 87, 88, 89, 97, 98, 104, 109, 112, 117, 119, 120, 121, 130, 132, 133, 135, 137, 152, 154, 156, 160, 161, 162, 164, 165, 168, 170, 177, 191, 197, 202, 203, 205, 206, 208, 209, 211, 214, 218, 222, 223, 227, 230, 232, 235, 238, 240, 241, 244, 246, 247, 248, 249, 251]

print(f"\nAnalyzing {len(top_miner_uids)} top miners...")

# Analyze datasets
hashes = {}
indices_data = {}
entry_counts = Counter()

for uid in top_miner_uids:
    path = f"data/miner_{uid}/data.jsonl"
    if not os.path.exists(path):
        continue
    
    miner_data = load_jsonl(path)
    h = get_dataset_hash(miner_data)
    hashes[uid] = h
    
    # Find eval indices
    indices = find_entry_positions(miner_data, eval_data)
    indices_data[uid] = indices
    
    # Count which eval entries are used
    for idx in indices:
        entry_counts[idx] += 1

print(f"\n{'='*80}")
print("HASH ANALYSIS - Are they using the same dataset?")
print(f"{'='*80}")

hash_counts = Counter(hashes.values())
unique_hashes = len(hash_counts)
most_common_hash = hash_counts.most_common(1)[0]

print(f"Unique dataset hashes: {unique_hashes}")
print(f"Most common hash used by: {most_common_hash[1]} miners")
print(f"Most common hash: {most_common_hash[0][:16]}...")

if unique_hashes == 1:
    print("\n⚠️  ALL TOP MINERS USE THE SAME DATASET!")
elif unique_hashes <= 5:
    print(f"\n⚠️  Only {unique_hashes} unique datasets across {len(top_miner_uids)} miners")
    print("Top hashes:")
    for h, count in hash_counts.most_common(5):
        print(f"  {h[:16]}...: {count} miners")
else:
    print(f"\n✓ Top miners use diverse datasets ({unique_hashes} unique)")

print(f"\n{'='*80}")
print("EVAL INDEX ANALYSIS - Which entries do they use?")
print(f"{'='*80}")

# Analyze which eval indices are most popular
all_indices = []
for uid, indices in indices_data.items():
    all_indices.extend(indices)

index_counts = Counter(all_indices)
most_used_indices = index_counts.most_common(20)

print("\nMost frequently used eval indices:")
for idx, count in most_used_indices[:20]:
    pct = (count / len(top_miner_uids)) * 100
    print(f"  Index {idx:4d}: {count:3d} miners ({pct:5.1f}%)")

# Check range distribution
print(f"\n{'='*80}")
print("RANGE ANALYSIS")
print(f"{'='*80}")

min_indices = [min(indices) for indices in indices_data.values() if indices]
max_indices = [max(indices) for indices in indices_data.values() if indices]

print(f"Min eval index range: {min(min_indices)} - {max(min_indices)}")
print(f"Max eval index range: {min(max_indices)} - {max(max_indices)}")
print(f"Average min index: {sum(min_indices)/len(min_indices):.1f}")
print(f"Average max index: {sum(max_indices)/len(max_indices):.1f}")

# Check for patterns - are they using contiguous ranges?
contiguous_count = 0
for uid, indices in indices_data.items():
    if indices == list(range(min(indices), max(indices)+1)):
        contiguous_count += 1

print(f"\nMiners using contiguous ranges: {contiguous_count}/{len(indices_data)}")

# Check overlap with user's miners
print(f"\n{'='*80}")
print("COMPARISON WITH USER'S MINERS")
print(f"{'='*80}")

user_uids = [96, 30]
for user_uid in user_uids:
    user_path = f"data/miner_{user_uid}/data.jsonl"
    if not os.path.exists(user_path):
        continue
    
    user_data = load_jsonl(user_path)
    user_hash = get_dataset_hash(user_data)
    user_indices = find_entry_positions(user_data, eval_data)
    
    # Check if any top miner uses same hash
    matching_hash = [uid for uid, h in hashes.items() if h == user_hash]
    
    if matching_hash:
        print(f"\nUser miner {user_uid}:")
        print(f"  ❌ Hash matches {len(matching_hash)} top miners: {matching_hash[:5]}")
    else:
        print(f"\nUser miner {user_uid}:")
        print(f"  ✓ Unique hash (different from all top miners)")
    
    # Check overlap in eval indices
    user_set = set(user_indices)
    overlaps = []
    for top_uid, top_indices in indices_data.items():
        top_set = set(top_indices)
        overlap = len(user_set & top_set)
        if overlap > 0:
            overlaps.append((top_uid, overlap))
    
    if overlaps:
        overlaps.sort(key=lambda x: x[1], reverse=True)
        max_overlap = overlaps[0][1]
        print(f"  Max overlap with top miners: {max_overlap}/250 entries")
        print(f"  Top 5 overlaps: {overlaps[:5]}")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")

# Check if there's a "magic" set of entries
highly_used = {idx: count for idx, count in entry_counts.items() if count >= len(top_miner_uids) * 0.5}
print(f"\nEval indices used by ≥50% of top miners: {len(highly_used)}")
if highly_used:
    print("These might be 'golden' entries:")
    for idx in sorted(highly_used.keys())[:20]:
        print(f"  Index {idx}: {highly_used[idx]}/{len(top_miner_uids)} miners")

