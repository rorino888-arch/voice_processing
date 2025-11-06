
## Installation

### Overview

In order to run FLock OFF, you will need to install the FLock OFF package and set up a Hugging Face account. The following instructions apply to all major operating systems.

### Clone the repository

```bash
git clone https://github.com/FLock-io/FLock-subnet.git
cd FLock-subnet
```

### Install dependencies with uv

1. Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Set up python environment and install dependencies: 

```bash
# Install dependencies
uv sync

# Install the package in development mode
uv pip install -e .
```

### Set up Hugging Face credentials

1. Create a Hugging Face account at huggingface.co
2. Generate an API token at huggingface.co/settings/tokens
3. Create a .env file in the project root:

```bash
HF_TOKEN=<YOUR_HUGGING_FACE_API_TOKEN>
```

4. Ensure the token has write access for miners (to upload datasets) and read access for validators

---

## How to Run FLock OFF

### Running a Miner

#### Prerequisites

Before mining, prepare the following:

1. **Hugging Face Account and Repository:**
   - Create a dataset repository on Hugging Face (e.g., yourusername/my-dataset)
   - Ensure your API token has write permissions

2. **Dataset Creation:**
   - Generate a dataset in JSONL format (one JSON object per line)
   - Each entry must follow this structure:

```json
{
  "system": "Optional system prompt (can be null)",
  "conversations": [
    {"role": "user", "content": "User input text"},
    {"role": "assistant", "content": "Assistant response text"}
  ]
}
```

**Example:**

```jsonl
{"system": "You are a helpful assistant.", "conversations": [{"role": "user", "content": "What is AI?"}, {"role": "assistant", "content": "AI is artificial intelligence."}]}
{"system": null, "conversations": [{"role": "user", "content": "Tell me a joke."}, {"role": "assistant", "content": "Why don't skeletons fight? They don't have guts."}]}
```

3. **Bittensor Wallet:** Register your hotkey on the subnet

#### Steps to Run a Miner

**Prepare Your Dataset:**
Use a script, scrape data, or manually curate data.jsonl. Aim for high-quality, diverse user-assistant pairs to maximize validator scores.

!!!!
generate new dataset for every miner
python3 prepare_unique_dataset.py

after generate the dataset, run miner script once.

**Run the Miner Script:**

```bash
python3 neurons/miner.py \
  --wallet.name reg \
  --wallet.hotkey m3 \
  --subtensor.network finney \
  --hf_repo_id darkhorse0811/p6-dataset \ (change just the dataset name for every miner.  dataset name: p6-dataset)
  --netuid 96 \
  --dataset_path ./data/1/data.jsonl \ (keep this for every miner)
  --logging.trace
```

Replace placeholders:

- `your_coldkey_name`: Your Bittensor wallet name
- `your_hotkey_name`: Your miner's hotkey
- `finney`: Network (use local for testing)
- `yourusername/my-dataset`: Your Hugging Face repo
- `netuid`: Subnet UID (adjust if different)
- `./data/data.jsonl`: Path to your dataset

**What Happens:**

- The script uploads data.jsonl to your Hugging Face repo
- It retrieves a commit hash (e.g., abc123...) and constructs a ModelId (e.g., yourusername/my-dataset:ORIGINAL_COMPETITION_ID:abc123...)
- It registers this metadata on the Bittensor chain (retrying every 120 seconds if the 20-minute commit cooldown applies)

**Tips:**

- Ensure your dataset is unique—validators penalize duplicates
- Monitor logs (--logging.trace) for upload or chain errors

### Running a Validator

#### Prerequisites

- **Hardware:** NVIDIA 4090 (24GB VRAM) recommended
- **Bittensor Wallet:** Register your hotkey on the subnet
- **Hugging Face Token:** Read access for downloading datasets

#### Steps to Run a Validator

**Ensure GPU Setup:**

- Install CUDA (e.g., 12.1) and cuDNN compatible with PyTorch
- Verify with nvidia-smi and torch.cuda.is_available()

**Run the Validator Script:**

```bash
python3 neurons/validator.py \
  --wallet.name your_coldkey_name \
  --netuid netuid \
  --logging.trace
```

Replace placeholders:

- `your_coldkey_name`: Your Bittensor wallet name
- `netuid`: Subnet UID

**What Happens:**

- Syncs the metagraph to identify active miners
- Selects up to 32 miners per epoch using an EvalQueue
- For each miner:
  - Retrieves metadata (e.g., ModelId) from the chain
  - Downloads the dataset from Hugging Face (e.g., yourusername/my-dataset:abc123...)
  - Downloads a fixed evaluation dataset (eval_data/data.jsonl)
  - Trains a LoRA model on the miner's dataset using Qwen/Qwen2.5-1.5B-Instruct
  - Evaluates loss on eval_data
  - Computes win rates, adjusts weights, and submits them to the chain

**Training Details:**

- **Model:** Qwen/Qwen2.5-1.5B-Instruct
- **LoRA Config:** Rank=16, Alpha=32, Dropout=0.1, targeting all linear layers
- **Training Args:** Batch size=2, gradient accumulation=4, 2 epochs, 4096-token context
- **Data Capacity:** With 24GB VRAM, ~10,000-20,000 rows (assuming ~256 tokens/row) per dataset, though limited by epoch duration and miner sample size (32)

**Tips:**

- Ensure ample storage for datasets and model checkpoints
- Use --logging.trace to debug training or chain issues

---

## Downloading All Miner Datasets

To download all miner datasets from the FLock subnet for analysis:

```bash
# Auto-detect FLock subnet and download all datasets
python3 download_all_miners.py --subtensor.network finney --logging.info

# Or specify netuid directly
python3 download_all_miners.py --netuid YOUR_NETUID --subtensor.network finney
```

The script will:
1. Connect to the Bittensor network
2. Fetch the metagraph for the FLock subnet
3. Retrieve all registered miners and their Hugging Face repository info
4. Download each miner's dataset to `~/data/miner_datasets/miner_<uid>/data.jsonl`
5. Provide a summary of successful downloads, failures, and skipped miners

For more details, see [README_DOWNLOAD.md](README_DOWNLOAD.md) and [example_usage.md](example_usage.md).

### Sorting Downloaded Datasets

After downloading, sort all datasets alphabetically for consistency:

```bash
# Sort all downloaded datasets
python3 sort_all_datasets.py

# Or specify a custom directory
python3 sort_all_datasets.py --data_dir ~/data/miner_datasets
```

This ensures consistent ordering across all datasets for easier comparison and duplicate detection. See [README_SORT.md](README_SORT.md) for details.

### Preparing a Unique Dataset for Mining

To create a unique dataset that avoids penalties:

```bash
# Create unique dataset (250 entries not used by other miners)
python3 prepare_unique_dataset.py --output_file ./data/my_unique_dataset.jsonl

# Verify it's unique
python3 check_datasets.py --data_dir ./data
```

This selects 250 entries from the evaluation dataset that haven't been used by other miners, ensuring your dataset will be properly evaluated by validators.

---

## What is a Dataset Competition Network?

FLock OFF is a decentralized subnet where miners compete to create high-quality datasets, and validators evaluate them using LoRA training. Rewards (in TAO) are distributed based on dataset performance, not raw compute power.

### Role of a Miner

**Task:** Create and upload datasets that improve model performance (e.g., low evaluation loss).

**Process:**

- Curate a dataset (e.g., conversational pairs in JSONL)
- Upload to Hugging Face with version control
- Register metadata on-chain (~0.01 TAO fee)

**Goal:** Outperform other miners in validator evaluations.

### Role of a Validator

**Task:** Assess dataset quality and set miner rewards.

**Process:**

- Fetch miner metadata from the chain
- Download datasets from Hugging Face
- Train LoRA on Qwen/Qwen2.5-1.5B-Instruct with each dataset
- Evaluate loss on a standard test set
- Compute win rates and update weights on-chain

**Goal:** Fairly reward miners based on dataset utility.

---

## Features of FLock OFF

### Hugging Face Integration

- **Storage:** Miners use Hugging Face repos for datasets (e.g., username/repo:commit)
- **Versioning:** Git-based commits ensure reproducibility
- **Accessibility:** Validators download datasets via the Hugging Face API

### LoRA Training Evaluation

- **Efficiency:** LoRA adapts Qwen/Qwen2.5-1.5B-Instruct with minimal parameters
- **Fairness:** Fixed training config ensures consistent evaluation
- **Capacity:** Validators can process ~10,000-20,000 rows per dataset on a 4090, depending on token length and epoch timing
- **Metrics:** Evaluation loss determines dataset quality, with duplicates penalized

