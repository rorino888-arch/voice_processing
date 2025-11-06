#!/usr/bin/env python3
"""Quick script to find miners by coldkey without downloading."""

import sys
import argparse
import bittensor as bt
from dotenv import load_dotenv

load_dotenv()

target_coldkey = "5CUZn2P8GNnXZnEqG4LFCSgohAgYDeH9q8d4GUzqyyBDjgg3"

print("Connecting to Bittensor...")
parser = argparse.ArgumentParser()
parser.add_argument("--netuid", type=int, default=96, help="Subnet UID")
bt.subtensor.add_args(parser)
bt.logging.add_args(parser)
config = bt.config(parser)
bt.logging(config=config)

subtensor = bt.subtensor(config=config)
print(f"Connected to: {subtensor.network}")

# Use netuid from config
netuid = config.netuid
print(f"\nFetching metagraph for netuid {netuid}...")
metagraph = subtensor.metagraph(netuid)

print(f"Total miners: {len(metagraph.uids)}")

# Find matching coldkeys
matching = []
for uid in metagraph.uids.tolist():
    coldkey = metagraph.coldkeys[uid]
    if coldkey == target_coldkey:
        matching.append(uid)
        hotkey = metagraph.hotkeys[uid]
        print(f"\nFound UID {uid}:")
        print(f"  Coldkey: {coldkey}")
        print(f"  Hotkey:  {hotkey[:20]}...")

print(f"\n{'='*60}")
print(f"Total miners found: {len(matching)}")
print(f"UIDs: {matching}")
print(f"{'='*60}")

