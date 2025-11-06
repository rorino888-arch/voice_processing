# Dataset Sorting Tool

## Overview

The `sort_all_datasets.py` script sorts all miner dataset files alphabetically by their JSON content. This is useful for:
- Consistent dataset ordering
- Easier comparison between datasets
- Detecting duplicates
- Standardizing dataset format

## Usage

### Basic Usage

```bash
# Sort all datasets in the default directory
python3 sort_all_datasets.py

# Or specify a custom directory
python3 sort_all_datasets.py --data_dir ~/data/miner_datasets
```

### How It Works

1. **Scans** all `miner_*/data.jsonl` files in the specified directory
2. **Reads** each JSONL file and parses the JSON lines
3. **Sorts** alphabetically using JSON string representation with sorted keys
4. **Writes** the sorted data back to the original file
5. **Reports** success/failure statistics

### Sorting Method

The script sorts by converting each JSON object to a string with sorted keys:
```python
sorted(data, key=lambda x: json.dumps(x, sort_keys=True))
```

This ensures:
- Consistent ordering regardless of key order in original JSON
- Alphabetical sorting based on JSON content
- Same content always sorts to the same position

## Example

### Before Sorting
```jsonl
{"system": "cat", "conversations": [{"role": "user", "content": "Meow"}]}
{"system": "bird", "conversations": [{"role": "user", "content": "Tweet"}]}
{"system": "dog", "conversations": [{"role": "user", "content": "Woof"}]}
```

### After Sorting
```jsonl
{"system": "bird", "conversations": [{"role": "user", "content": "Tweet"}]}
{"system": "cat", "conversations": [{"role": "user", "content": "Meow"}]}
{"system": "dog", "conversations": [{"role": "user", "content": "Woof"}]}
```

## Output

```
Scanning directory: ~/data/miner_datasets
================================================================================
Found 10 miner directories

Sorting: ~/data/miner_datasets/miner_1/data.jsonl
  → Sorted 250 entries
Sorting: ~/data/miner_datasets/miner_2/data.jsonl
  → Sorted 250 entries
...

================================================================================
SORTING SUMMARY
================================================================================
Total miner directories: 10
Successfully sorted: 8
Failed: 0
Skipped (no file): 2
================================================================================
```

## Safety

- **No backup**: The script modifies files in place. Make sure you have backups if needed
- **Idempotent**: Running multiple times produces the same result
- **Error handling**: Continues processing other files even if one fails
- **Validation**: Checks JSON validity before processing

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Use Cases

### 1. Standardize Dataset Order

After downloading datasets from different miners, ensure they're all in a consistent format:
```bash
python3 sort_all_datasets.py
```

### 2. Prepare for Comparison

Sort datasets before comparing them:
```bash
# Sort all datasets
python3 sort_all_datasets.py

# Then compare two datasets
diff miner_1/data.jsonl miner_2/data.jsonl
```

### 3. Detect Duplicates

Sorted datasets make it easier to spot exact duplicates:
```python
import json
from pathlib import Path

# Read two sorted datasets
ds1 = [json.loads(l) for l in Path("miner_1/data.jsonl").read_text().splitlines()]
ds2 = [json.loads(l) for l in Path("miner_2/data.jsonl").read_text().splitlines()]

# Compare line by line
duplicates = sum(1 for a, b in zip(ds1, ds2) if a == b)
print(f"Found {duplicates} duplicate entries")
```

### 4. Pre-processing for ML

Before training models, standardize dataset order:
```bash
python3 sort_all_datasets.py --data_dir ~/data/miner_datasets
```

## Integration with Download Script

Use with `download_all_miners.py`:

```bash
# Download all datasets
python3 download_all_miners.py --subtensor.network finney

# Sort all downloaded datasets
python3 sort_all_datasets.py
```

## Troubleshooting

### "Directory does not exist"
```bash
# Make sure the directory path is correct
python3 sort_all_datasets.py --data_dir /correct/path
```

### "Error parsing line"
The file might have invalid JSON. Check:
```bash
# Find the problematic file
head -n 5 ~/data/miner_datasets/miner_X/data.jsonl

# Validate JSON
python3 -m json.tool miner_X/data.jsonl
```

### "Skipped (no file)"
The miner directory exists but has no `data.jsonl`. This is normal if some miners haven't uploaded datasets yet.

## Performance

- **Speed**: ~1-2 seconds per 250-entry file
- **Memory**: Minimal (processes files one at a time)
- **I/O**: Reads and writes each file once

For 8 datasets of 250 entries each, total time is ~10-15 seconds.

## See Also

- `download_all_miners.py` - Download datasets from miners
- `README_DOWNLOAD.md` - Download documentation
- `example_usage.md` - Usage examples

