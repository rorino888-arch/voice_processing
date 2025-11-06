# Quick Start: Download All Miner Datasets

## TL;DR

```bash
# 1. Set up your Hugging Face token
echo "HF_TOKEN=your_token_here" > .env

# 2. Download all miner datasets
python3 download_all_miners.py --subtensor.network finney --logging.info

# 3. Find your datasets
ls -lh ~/data/miner_datasets/
```

That's it! The script will auto-detect the FLock subnet and download everything.

## Full Command Options

```bash
python3 download_all_miners.py \
  --netuid 123 \                    # Optional: specify netuid (auto-detected if omitted)
  --subtensor.network finney \      # finney|test|local
  --data_dir ~/data/miner_datasets \ # Where to save datasets
  --cache_dir ~/data/hf_cache \      # HF cache directory
  --logging.info                     # info|debug|trace
```

## Networks

- `finney` - Main production network
- `test` - Test network
- `local` - Local development

## Output Location

Datasets are saved to: `~/data/miner_datasets/miner_<uid>/data.jsonl`

## Need Help?

- **Don't know netuid?** Run: `python3 find_netuid.py --subtensor.network finney`
- **More details?** See: `README_DOWNLOAD.md`
- **Examples?** See: `example_usage.md`
- **Summary?** See: `DOWNLOAD_SUMMARY.md`

## Common Issues

| Problem | Solution |
|---------|----------|
| "HF_TOKEN not found" | Add token to `.env` file |
| "Can't find subnet" | Specify `--netuid` manually |
| "Connection timeout" | Try `--subtensor.chain_endpoint` |
| "No miners found" | Check network: use `--subtensor.network test` first |

## What You Get

After downloading, you'll have:
```
~/data/miner_datasets/
├── miner_0/data.jsonl    # First miner's dataset
├── miner_1/data.jsonl    # Second miner's dataset
└── ...
```

Each `data.jsonl` file contains conversational data in this format:
```jsonl
{"system": "You are a helpful assistant.", "conversations": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Next Steps

1. **Analyze quality**: Check dataset diversity and uniqueness
2. **Detect duplicates**: Use `count_similar()` from validator
3. **Train models**: Aggregate datasets for ML training
4. **Compare miners**: See `DOWNLOAD_SUMMARY.md` for analysis ideas

---

**Full Documentation**: `README_DOWNLOAD.md`  
**Examples**: `example_usage.md`  
**Overview**: `DOWNLOAD_SUMMARY.md`

