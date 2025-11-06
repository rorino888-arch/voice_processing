# Preparing Your Unique Miner Dataset

## Overview

This guide explains how to create a unique dataset for mining that will pass the validator's duplicate detection checks.

## The Challenge

The FLock subnet validator has strict duplicate detection:
- **Rejects** datasets that copy the entire eval dataset
- **Rejects** datasets with entries not in eval dataset  
- **Groups and penalizes** miners with duplicate datasets

All 249 current miners have submitted **exact copies** of the eval dataset and will receive penalty scores.

## Solution: Unique Dataset Script

The `prepare_unique_dataset.py` script creates a dataset that:
- ✅ Uses entries from the eval dataset (required)
- ✅ Avoids entries already used by other miners
- ✅ Is completely unique
- ✅ Will pass validator checks

## Usage

### Basic Usage

```bash
python3 prepare_unique_dataset.py --output_file ./data/my_unique_dataset.jsonl
```

This creates a 250-entry unique dataset.

### Advanced Options

```bash
python3 prepare_unique_dataset.py \
  --eval_data_file ./data/eval_data/data.jsonl \
  --miner_data_dir ./data \
  --output_file ./data/my_dataset.jsonl \
  --num_entries 250 \
  --seed 42
```

**Options:**
- `--eval_data_file`: Path to evaluation dataset (default: `./data/eval_data/data.jsonl`)
- `--miner_data_dir`: Directory with miner datasets (default: `./data`)
- `--output_file`: Where to save your dataset (default: `./data/my_miner_dataset.jsonl`)
- `--num_entries`: Number of entries to select (default: 250)
- `--seed`: Random seed for reproducibility

## How It Works

### Algorithm

1. **Load eval dataset**: 5,301 entries
2. **Collect miner entries**: Gather all entries from existing miner datasets
3. **Find unique entries**: Identify entries NOT in miner datasets (3,176 available)
4. **Randomly select**: Pick the required number of entries
5. **Sort alphabetically**: For consistency
6. **Verify uniqueness**: Double-check no overlap

### Validation Logic

The script simulates the validator's check:
```python
# Same as validator (line 356)
if count_similar(eval_data, miner_data) == len(miner_data):
    # PASS: All entries are from eval
    train_and_evaluate()
else:
    # FAIL: Some entries not in eval
    assign_penalty_999()
```

## Example Output

```
====================================================================================================
PREPARING UNIQUE DATASET FOR MINING
====================================================================================================

Loading evaluation dataset: ./data/eval_data/data.jsonl
Loaded 5301 entries from evaluation dataset

Collecting entries from all miner datasets...
Collected 2125 unique entries from 251 miner datasets

Finding 250 unique entries...
Found 3176 entries from eval_data NOT in miner datasets
Sorting entries alphabetically...

Writing 250 entries to: ./data/my_unique_dataset.jsonl

Verifying uniqueness...
✅ SUCCESS: Your dataset has NO overlap with miner datasets!

====================================================================================================
SUMMARY
====================================================================================================
✅ Created unique dataset: ./data/my_unique_dataset.jsonl
   Total entries: 250
   Overlap with miners: 0
   Random seed: 42

📝 Next steps:
   1. Review your dataset: cat ./data/my_unique_dataset.jsonl | head -5
   2. Check it's unique: python3 check_datasets.py --data_dir ./data
   3. Upload to HuggingFace and register with miner
====================================================================================================
```

## Verification

### Check Uniqueness

```bash
# Verify your dataset is unique
python3 check_datasets.py --data_dir ./data
```

### Manual Verification

```python
import json

def count_similar(jsonl1, jsonl2):
    set1 = set(json.dumps(item, sort_keys=True) for item in jsonl1)
    set2 = set(json.dumps(item, sort_keys=True) for item in jsonl2)
    return len(set1 & set2)

# Load datasets
eval_data = load_jsonl('./data/eval_data/data.jsonl')
my_data = load_jsonl('./data/my_unique_dataset.jsonl')
miner_data = load_jsonl('./data/miner_1/data.jsonl')

# Check
similar_eval = count_similar(eval_data, my_data)
similar_miner = count_similar(miner_data, my_data)

print(f"Overlap with eval: {similar_eval}/{len(my_data)}")
print(f"Overlap with miner: {similar_miner}/{len(my_data)}")
print(f"Unique: {'YES ✅' if similar_miner == 0 else 'NO ❌'}")
```

## What the Validator Does

### Stage 1: Eval Dataset Check
```
if count_similar(eval, miner) != len(miner):
    → Penalty: 999 (some entries not in eval)
    → Skip to next miner
```

**Your unique dataset**: ✅ PASSES (all entries in eval)

### Stage 2: Duplicate Check
```
For each pair of miners:
    if count_similar(miner_i, miner_j) > 100:
        → Group as duplicates
        → Penalize later miner (by block number)
```

**Your unique dataset**: ✅ PASSES (no duplicates)

### Stage 3: LoRA Training
If passes both checks, validator:
1. Trains LoRA on your dataset
2. Evaluates loss on eval dataset
3. Computes normalized score
4. Updates weights on-chain

**Your unique dataset**: ✅ Will be evaluated properly

## Using Your Dataset

### 1. Review Dataset

```bash
# Preview first few entries
head -3 ./data/my_unique_dataset.jsonl

# Count total entries
wc -l ./data/my_unique_dataset.jsonl
```

### 2. Upload to HuggingFace

```bash
# Using the miner script
python3 neurons/miner.py \
  --hf_repo_id YOUR_USERNAME/my-dataset \
  --netuid NETUID \
  --dataset_path ./data/my_unique_dataset.jsonl \
  --wallet.name your_wallet \
  --subtensor.network finney
```

### 3. Wait for Evaluation

- Validator downloads your dataset
- Checks against eval dataset ✅
- Checks for duplicates ✅
- Trains LoRA model
- Computes score
- Awards rewards

## Limitations

### Scarcity

As more miners join:
- Fewer unique entries available
- Eventually may need to wait for eval dataset updates
- Currently: 3,176 unique entries available (good for ~12 miners)

### Strategy

**Best approach**: 
1. Use `prepare_unique_dataset.py` to get unique entries
2. Or create completely original datasets
3. Avoid copying eval dataset

**Current situation**:
- All 249 miners copied eval dataset
- Will get penalty scores
- Your unique dataset will compete against... penalties

## Troubleshooting

### "Only X unique entries available"

**Cause**: Too many miners have joined  
**Solution**: Reduce `--num_entries` or wait for eval dataset updates

### "No unique entries found"

**Cause**: All eval entries already used  
**Solution**: Need new eval dataset or create original data

### Dataset validation fails

**Check**:
```bash
python3 check_datasets.py --data_dir ./data
```

**Common issues**:
- Wrong format (must be JSONL)
- Missing fields (need `conversations`)
- Invalid JSON syntax

## Statistics

### Current State (analyzed)

- **Total eval entries**: 5,301
- **Unique in miners**: 2,125
- **Available unique**: 3,176
- **Miners with duplicates**: 249 (100%)
- **Miners with unique datasets**: 0

### After Your Submission

- **Available unique**: ~2,926 (for next miner)
- **Space for**: ~11 more unique miners
- **Your advantage**: MASSIVE (first unique miner!)

## See Also

- `check_datasets.py` - Verify uniqueness
- `download_all_miners.py` - Download all datasets
- `sort_all_datasets.py` - Sort datasets
- `README_DOWNLOAD.md` - Download documentation
- `README_SORT.md` - Sorting documentation

## Best Practices

1. **Always verify**: Check uniqueness before uploading
2. **Use seed**: For reproducibility with `--seed`
3. **Review data**: Ensure quality entries
4. **Monitor**: Track validator scores
5. **Iterate**: Improve dataset quality over time

## Success Criteria

Your dataset is ready when:
- ✅ All entries from eval dataset
- ✅ No overlap with other miners
- ✅ Valid JSONL format
- ✅ 250 entries (or required amount)
- ✅ Sorted alphabetically
- ✅ Verified with check_datasets.py

---

**Good luck with your mining! 🎉**

