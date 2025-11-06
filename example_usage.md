# Example Usage: Downloading All Miner Datasets

## Basic Usage

### Option 1: Auto-detect the FLock subnet

```bash
# Let the script find the FLock subnet automatically
python3 download_all_miners.py \
  --subtensor.network finney \
  --logging.info
```

### Option 2: Specify the netuid

```bash
# If you know the netuid (example: 123)
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network finney \
  --logging.info
```

### Option 3: Custom directories

```bash
# Download to custom directories
python3 download_all_miners.py \
  --netuid 123 \
  --data_dir /path/to/my/datasets \
  --cache_dir /path/to/my/cache \
  --subtensor.network finney \
  --logging.debug
```

## Network Options

### Main Network (Finney)
```bash
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network finney \
  --logging.info
```

### Test Network
```bash
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network test \
  --logging.info
```

### Local Development
```bash
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network local \
  --logging.debug
```

## Finding Your Netuid

If you don't know the netuid:

```bash
# Search all subnets on finney
python3 find_netuid.py --subtensor.network finney

# Search all subnets on test
python3 find_netuid.py --subtensor.network test
```

This will list all subnets and help you identify which one is the FLock subnet.

## Expected Output

```
2024-11-02 16:37:00 - INFO: Starting to download all miner datasets
2024-11-02 16:37:01 - INFO: Connecting to Bittensor network...
2024-11-02 16:37:02 - SUCCESS: Connected to network: finney
2024-11-02 16:37:02 - INFO: Fetching metagraph for netuid: 123
2024-11-02 16:37:05 - SUCCESS: Retrieved metagraph with 42 miners
2024-11-02 16:37:05 - INFO: Found 42 registered miners
2024-11-02 16:37:06 - INFO: UID 0: Downloading user123/my-dataset@abc123def456...
2024-11-02 16:37:18 - SUCCESS: UID 0: Downloaded 250 data entries from user123/my-dataset
2024-11-02 16:37:19 - WARNING: UID 1: No metadata found (miner hasn't uploaded a dataset)
2024-11-02 16:37:20 - INFO: UID 2: Downloading anotheruser/dataset@xyz789...
...
2024-11-02 17:05:30 - ERROR: UID 41: Failed to download dataset: Repository not found
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

### "Could not find FLock subnet automatically"

Manually specify the netuid:
```bash
python3 download_all_miners.py --netuid YOUR_NETUID --subtensor.network finney
```

Or find it using:
```bash
python3 find_netuid.py --subtensor.network finney
```

### "HF_TOKEN not found"

Create a `.env` file with your Hugging Face token:
```bash
echo "HF_TOKEN=your_token_here" > .env
```

Or export it:
```bash
export HF_TOKEN=your_token_here
python3 download_all_miners.py --netuid 123 --subtensor.network finney
```

### "Connection timeout"

Try a different chain endpoint:
```bash
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network finney \
  --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443
```

## After Downloading

Datasets will be in:
```
~/data/miner_datasets/
├── miner_0/
│   └── data.jsonl  (250 lines)
├── miner_2/
│   └── data.jsonl  (180 lines)
├── miner_3/
│   └── data.jsonl  (300 lines)
└── ...
```

You can then:
- Analyze the datasets
- Check for duplicates
- Train models on subsets
- Compare miner quality

## Advanced: Use as Python Module

```python
from flockoff.validator.chain import retrieve_model_metadata
from flockoff.validator.trainer import download_dataset
import bittensor as bt

# Connect to network
config = bt.config()
subtensor = bt.subtensor(config)
metagraph = subtensor.metagraph(YOUR_NETUID)

# Download a specific miner
uid = 0
metadata = retrieve_model_metadata(
    subtensor, YOUR_NETUID, metagraph.hotkeys[uid]
)
download_dataset(
    metadata.id.namespace,
    metadata.id.commit,
    local_dir=f"miner_{uid}",
    cache_dir="~/data/hf_cache"
)
```

## See Also

- `README.md` - Main project documentation
- `README_DOWNLOAD.md` - Detailed download documentation
- `neurons/validator.py` - How validators download datasets
- `flockoff/validator/trainer.py` - Download implementation

