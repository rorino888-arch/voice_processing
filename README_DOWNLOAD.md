# Downloading All Miner Datasets

This document explains how to download all miner datasets from the FLock subnet.

## Quick Start

To download all miner datasets:

```bash
python3 download_all_miners.py \
  --netuid <YOUR_NETUID> \
  --subtensor.network finney \
  --data_dir ~/data/miner_datasets \
  --cache_dir ~/data/hf_cache \
  --logging.debug
```

### Finding the NetUID

If you don't know the netuid for the FLock subnet:

```bash
python3 find_netuid.py --subtensor.network finney
```

Or check the [Bittensor subnets page](https://taostats.io/subnets/) or the FLock community Discord/Telegram.

## What This Does

1. **Connects to the Bittensor network** - Fetches the metagraph for the FLock subnet
2. **Retrieves all miners** - Gets the list of all registered miners (UIDs and hotkeys)
3. **Downloads metadata** - For each miner, retrieves their Hugging Face repository information
4. **Downloads datasets** - Downloads each miner's dataset from Hugging Face to local storage
5. **Provides summary** - Shows statistics on successful downloads, failures, and skipped miners

## Network Options

- `--subtensor.network finney` - Main network
- `--subtensor.network test` - Test network
- `--subtensor.network local` - Local development

## Directory Structure

After downloading, datasets will be organized like this:

```
~/data/miner_datasets/
├── miner_0/
│   └── data.jsonl
├── miner_1/
│   └── data.jsonl
├── miner_2/
│   └── data.jsonl
└── ...
```

## Requirements

1. **Hugging Face Token** - Set `HF_TOKEN` in your `.env` file
2. **Bittensor Setup** - Validator wallet configured (optional, can run without)
3. **Storage Space** - Each dataset may be 1-100MB, plan for 1GB+

## Expected Output

```
2024-11-02 16:37:00 - INFO: Starting to download all miner datasets
2024-11-02 16:37:01 - SUCCESS: Connected to network: finney
2024-11-02 16:37:02 - SUCCESS: Retrieved metagraph with 42 miners
2024-11-02 16:37:03 - INFO: UID 0: Downloading user123/dataset@abc123...
2024-11-02 16:37:15 - SUCCESS: UID 0: Downloaded 250 data entries from user123/dataset
...
================================================================================
DOWNLOAD SUMMARY
================================================================================
Total miners: 42
Successfully downloaded: 38
Failed: 2
Skipped (no metadata): 2
================================================================================
```

## Troubleshooting

### "HF_TOKEN not found"
Set your Hugging Face token in `.env`:
```
HF_TOKEN=hf_your_token_here
```

### "Failed to download dataset"
Common causes:
- Miner hasn't uploaded a dataset yet
- Hugging Face repository doesn't exist
- Network connectivity issues
- Insufficient permissions on token

### "Too many API requests"
- The script respects Hugging Face rate limits
- Add delays between downloads if needed

## Advanced Usage

### Skip Already Downloaded Datasets

The script automatically skips datasets that are already downloaded. To force re-download:

```bash
# Edit download_all_miners.py and change force=False to force=True
```

### Download Only Specific Miners

Edit the script to filter UIDs:
```python
for uid in current_uids:
    if uid not in [0, 1, 2]:  # Only download these UIDs
        continue
```

### Parallel Downloads

For faster downloads, modify to use threading:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download_miner_dataset, current_uids)
```

## Alternative: Use Validator's Download Logic

The validator already has download logic. You can use it programmatically:

```python
from flockoff.validator.trainer import download_dataset

download_dataset(
    namespace="user123/dataset",
    revision="abc123...",
    local_dir="miner_0",
    cache_dir="~/data/hf_cache",
    force=False
)
```

## Next Steps

After downloading all datasets:
1. Analyze dataset quality and diversity
2. Check for duplicates using `count_similar()` from `validator_utils.py`
3. Train models on subsets or all datasets
4. Compare miner performance

## Script Details

The `download_all_miners.py` script:
- Uses the same download logic as the validator
- Respects Hugging Face caching
- Provides detailed progress logging
- Handles errors gracefully
- Doesn't require wallet registration (just needs network access)

