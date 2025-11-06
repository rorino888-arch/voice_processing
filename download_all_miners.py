#!/usr/bin/env python3
"""
Script to download all miner datasets from the FLock subnet.
This connects to the Bittensor network, retrieves all miner metadata, and downloads their datasets from HuggingFace.
"""

import os
import argparse
import bittensor as bt
from dotenv import load_dotenv
from flockoff.validator.chain import retrieve_model_metadata
from flockoff.validator.trainer import download_dataset
from flockoff.constants import Competition

load_dotenv()


def download_all_miners():
    """Download datasets from all registered miners."""
    bt.logging.info("Starting to download all miner datasets")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--netuid", type=int, default=None, help="The subnet UID. If not provided, will search for FLock subnet.")
    parser.add_argument("--data_dir", type=str, default="~/data/miner_datasets", help="Directory to store miner datasets.")
    parser.add_argument("--cache_dir", type=str, default="~/data/hf_cache", help="Directory for HF cache.")
    
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)
    config = bt.config(parser)
    
    bt.logging(config=config)
    
    # Expand home directory paths
    if config.data_dir and config.data_dir.startswith("~"):
        config.data_dir = os.path.expanduser(config.data_dir)
    if config.cache_dir and config.cache_dir.startswith("~"):
        config.cache_dir = os.path.expanduser(config.cache_dir)
    
    # Initialize subtensor connection
    bt.logging.info("Connecting to Bittensor network...")
    subtensor = bt.subtensor(config=config)
    bt.logging.success(f"Connected to network: {subtensor.network}")
    
    # Auto-detect netuid if not provided
    if config.netuid is None:
        bt.logging.info("Netuid not provided, searching for FLock subnet...")
        subnets = subtensor.get_subnets()
        bt.logging.info(f"Found {len(subnets)} subnets, checking each...")
        
        # Try to find the FLock subnet by checking which one has miners with HF datasets
        found_netuid = None
        for netuid in subnets:
            try:
                metagraph = subtensor.metagraph(netuid)
                if len(metagraph.uids) > 0:
                    # Check first miner to see if they have HF metadata
                    test_metadata = retrieve_model_metadata(
                        subtensor, netuid, metagraph.hotkeys[0]
                    )
                    if test_metadata is not None:
                        bt.logging.info(f"Found potential FLock subnet at netuid {netuid} with {len(metagraph.uids)} miners")
                        found_netuid = netuid
                        break
            except Exception as e:
                bt.logging.debug(f"Netuid {netuid}: {e}")
                continue
        
        if found_netuid is None:
            bt.logging.error("Could not find FLock subnet automatically. Please specify --netuid manually.")
            return
        config.netuid = found_netuid
        bt.logging.success(f"Using netuid: {config.netuid}")
    
    # Get metagraph
    bt.logging.info(f"Fetching metagraph for netuid: {config.netuid}")
    metagraph = subtensor.metagraph(config.netuid)
    bt.logging.success(f"Retrieved metagraph with {len(metagraph.uids)} miners")
    
    # Get all UIDs
    current_uids = metagraph.uids.tolist()
    hotkeys = metagraph.hotkeys
    bt.logging.info(f"Found {len(current_uids)} registered miners")
    
    # Download datasets for all miners
    downloaded = 0
    failed = 0
    skipped = 0
    
    for uid in current_uids:
        try:
            # Get miner metadata
            metadata = retrieve_model_metadata(subtensor, config.netuid, hotkeys[uid])
            
            if metadata is None:
                bt.logging.warning(f"UID {uid}: No metadata found (miner hasn't uploaded a dataset)")
                skipped += 1
                continue
            
            # Create directory for this miner
            miner_data_dir = os.path.join(config.data_dir, f"miner_{uid}")
            
            # Download the dataset
            bt.logging.info(f"UID {uid}: Downloading {metadata.id.namespace}@{metadata.id.commit}")
            download_dataset(
                metadata.id.namespace,
                metadata.id.commit,
                local_dir=miner_data_dir,
                cache_dir=config.cache_dir,
                force=False  # Don't force re-download if already exists
            )
            
            # Verify download
            data_file = os.path.join(miner_data_dir, "data.jsonl")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    lines = len(f.readlines())
                bt.logging.success(f"UID {uid}: Downloaded {lines} data entries from {metadata.id.namespace}")
                downloaded += 1
            else:
                bt.logging.error(f"UID {uid}: Downloaded but data.jsonl not found")
                failed += 1
                
        except Exception as e:
            bt.logging.error(f"UID {uid}: Failed to download dataset: {e}")
            failed += 1
    
    # Summary
    bt.logging.info("=" * 80)
    bt.logging.info("DOWNLOAD SUMMARY")
    bt.logging.info("=" * 80)
    bt.logging.info(f"Total miners: {len(current_uids)}")
    bt.logging.info(f"Successfully downloaded: {downloaded}")
    bt.logging.info(f"Failed: {failed}")
    bt.logging.info(f"Skipped (no metadata): {skipped}")
    bt.logging.info("=" * 80)


if __name__ == "__main__":
    download_all_miners()

