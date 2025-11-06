# FLock Subnet - Download Tools Summary

## Overview

I've created a comprehensive set of tools to download all miner datasets from the FLock subnet. These tools allow you to easily fetch and analyze all datasets uploaded by miners on the Bittensor subnet.

## Files Created

### 1. `download_all_miners.py` - Main Download Script

**Purpose**: Downloads all miner datasets from the FLock subnet

**Features**:
- ✅ Auto-detects FLock subnet (if netuid not specified)
- ✅ Connects to Bittensor network (finney/test/local)
- ✅ Retrieves all registered miners from metagraph
- ✅ Downloads datasets from HuggingFace
- ✅ Provides detailed progress logging
- ✅ Shows comprehensive summary statistics
- ✅ Handles errors gracefully

**Usage**:
```bash
# Auto-detect netuid
python3 download_all_miners.py --subtensor.network finney --logging.info

# Specify netuid
python3 download_all_miners.py --netuid 123 --subtensor.network finney --logging.info
```

### 2. `find_netuid.py` - Helper Script

**Purpose**: Finds the netuid for FLock subnet

**Features**:
- Lists all subnets on the network
- Shows miner counts for each subnet
- Helps identify which subnet is FLock

**Usage**:
```bash
python3 find_netuid.py --subtensor.network finney
```

### 3. Documentation Files

#### `README_DOWNLOAD.md`
Comprehensive documentation including:
- Detailed usage instructions
- Network options (finney/test/local)
- Directory structure
- Troubleshooting guide
- Advanced usage examples
- Alternative approaches

#### `example_usage.md`
Quick reference with:
- Common usage patterns
- Expected output examples
- Network-specific commands
- Troubleshooting tips

#### `DOWNLOAD_SUMMARY.md` (this file)
Overview of all created tools

### 4. Updated `README.md`

Added a new section "Downloading All Miner Datasets" to the main README with:
- Quick start commands
- What the script does
- Links to detailed documentation

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  download_all_miners.py                                 │
│                                                         │
│  1. Connect to Bittensor Network                       │
│     (finney/test/local)                                 │
│                                                         │
│  2. Fetch Metagraph                                     │
│     - All registered miners                             │
│     - UIDs and hotkeys                                  │
│                                                         │
│  3. Retrieve Metadata                                   │
│     - For each miner, get HF repo info                  │
│     - Parse ModelId (namespace:comp_id:commit)         │
│                                                         │
│  4. Download Datasets                                   │
│     - From HuggingFace to local storage                 │
│     - Cache for efficiency                              │
│     - Respect rate limits                               │
│                                                         │
│  5. Verify & Report                                     │
│     - Count data entries                                │
│     - Show summary statistics                           │
└─────────────────────────────────────────────────────────┘
```

### Key Functions Used

1. **`retrieve_model_metadata()`** - From `flockoff/validator/chain.py`
   - Gets miner's HF repository metadata from chain
   - Returns ModelId with namespace, competition_id, commit

2. **`download_dataset()`** - From `flockoff/validator/trainer.py`
   - Downloads dataset from HuggingFace
   - Handles caching and revision tracking
   - Uses ScoreDB for persistence

3. **`subtensor.metagraph()`** - Bittensor API
   - Fetches all registered miners
   - Provides UIDs and hotkeys

## Example Output

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
2024-11-02 16:37:32 - SUCCESS: UID 2: Downloaded 180 data entries from anotheruser/dataset
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

## Directory Structure After Download

```
~/data/
├── miner_datasets/           # Downloaded miner datasets
│   ├── miner_0/
│   │   └── data.jsonl        # 250 conversational data entries
│   ├── miner_2/
│   │   └── data.jsonl        # 180 data entries
│   ├── miner_3/
│   │   └── data.jsonl        # 300 data entries
│   └── ...
└── hf_cache/                 # HuggingFace cache
    ├── datasets/             # Downloaded HF datasets
    └── models/               # Model files cache
```

## Requirements

- ✅ Python 3.10-3.12
- ✅ Bittensor library
- ✅ HuggingFace token in `.env` file
- ✅ Network access to Bittensor chain
- ✅ Sufficient storage space (1GB+ recommended)

## Network Configuration

### Main Network (Finney)
```bash
python3 download_all_miners.py --netuid 123 --subtensor.network finney
```

### Test Network
```bash
python3 download_all_miners.py --netuid 123 --subtensor.network test
```

### Local Development
```bash
python3 download_all_miners.py --netuid 123 --subtensor.network local
```

## Auto-Detection Feature

The script can automatically find the FLock subnet by:
1. Getting all subnets on the network
2. Checking each subnet for miners
3. Testing if miners have HuggingFace metadata
4. Selecting the first subnet with HF datasets

This eliminates the need to manually look up the netuid!

## Integration with Existing Code

The download script reuses code from the validator:
- Same metadata retrieval logic
- Same download function
- Same caching mechanism
- Same error handling

This ensures consistency and reliability.

## Use Cases

1. **Dataset Analysis**: Download all datasets for quality analysis
2. **Research**: Study patterns across multiple miners
3. **Benchmarking**: Compare miner performance
4. **Duplicate Detection**: Find copied or similar datasets
5. **Model Training**: Aggregate datasets for training
6. **Monitoring**: Track changes over time

## Troubleshooting

### Common Issues

1. **"HF_TOKEN not found"**
   ```bash
   # Add to .env file
   echo "HF_TOKEN=your_token_here" >> .env
   ```

2. **"Could not find FLock subnet automatically"**
   ```bash
   # Find manually
   python3 find_netuid.py --subtensor.network finney
   
   # Then specify
   python3 download_all_miners.py --netuid FOUND_NETUID
   ```

3. **"Connection timeout"**
   ```bash
   # Try different endpoint
   python3 download_all_miners.py --netuid 123 \
     --subtensor.chain_endpoint wss://entrypoint-finney.opentensor.ai:443
   ```

## Future Enhancements

Possible improvements:
- [ ] Parallel downloads for faster fetching
- [ ] Resume capability for interrupted downloads
- [ ] Filter by date or quality metrics
- [ ] Export to different formats (CSV, Parquet)
- [ ] Diff analysis between versions
- [ ] Web UI for browsing datasets

## Testing

To test the scripts:

```bash
# Test on testnet first
python3 download_all_miners.py \
  --netuid 123 \
  --subtensor.network test \
  --logging.debug

# Verify downloads
ls -lh ~/data/miner_datasets/

# Check data quality
head ~/data/miner_datasets/miner_0/data.jsonl
```

## Contributing

If you find issues or have suggestions:
1. Check existing issues on GitHub
2. Create detailed bug reports
3. Suggest enhancements
4. Submit pull requests

## License

MIT License - Same as the main project

## Related Documentation

- `README.md` - Main project documentation
- `README_DOWNLOAD.md` - Detailed download guide
- `example_usage.md` - Usage examples
- `neurons/validator.py` - Validator implementation
- `flockoff/validator/trainer.py` - Download implementation

## Summary

These tools provide a complete solution for downloading and analyzing all miner datasets from the FLock subnet. The implementation is robust, well-documented, and integrates seamlessly with the existing codebase.

**Key Features**:
- ✅ Simple to use
- ✅ Auto-detection of subnet
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Detailed documentation
- ✅ Consistent with validator code

Enjoy exploring the FLock datasets! 🚀

