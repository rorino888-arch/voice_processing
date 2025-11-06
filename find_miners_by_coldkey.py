#!/usr/bin/env python3
"""
Script to find all miners by coldkey and download/analyze their datasets.
"""

import os
import argparse
import bittensor as bt
from dotenv import load_dotenv
from flockoff.validator.chain import retrieve_model_metadata
from flockoff.validator.trainer import download_dataset

load_dotenv()


def find_and_download_by_coldkey(target_coldkey: str, netuid: int = None, data_dir: str = "./data"):
    """Find all miners with a specific coldkey and download their datasets."""
    bt.logging.info(f"Searching for miners with coldkey: {target_coldkey}")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--netuid", type=int, default=netuid, help="The subnet UID.")
    parser.add_argument("--data_dir", type=str, default=data_dir, help="Directory to store miner datasets.")
    parser.add_argument("--cache_dir", type=str, default=None, help="Directory for HF cache.")
    
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
        
        found_netuid = None
        for netuid in subnets:
            try:
                metagraph = subtensor.metagraph(netuid)
                if len(metagraph.uids) > 0:
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
    
    # Find all UIDs with matching coldkey
    matching_uids = []
    current_uids = metagraph.uids.tolist()
    coldkeys = metagraph.coldkeys
    
    for uid in current_uids:
        coldkey = coldkeys[uid]
        if coldkey == target_coldkey:
            matching_uids.append(uid)
            bt.logging.info(f"Found UID {uid} with matching coldkey")
    
    if not matching_uids:
        bt.logging.warning(f"No miners found with coldkey: {target_coldkey}")
        return []
    
    bt.logging.success(f"Found {len(matching_uids)} miners with coldkey {target_coldkey}: {matching_uids}")
    
    # Download datasets for matching miners
    downloaded = []
    failed = []
    
    for uid in matching_uids:
        try:
            hotkey = metagraph.hotkeys[uid]
            metadata = retrieve_model_metadata(subtensor, config.netuid, hotkey)
            
            if metadata is None:
                bt.logging.warning(f"UID {uid}: No metadata found (miner hasn't uploaded a dataset)")
                failed.append((uid, "No metadata"))
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
                force=True  # Force re-download to get latest
            )
            
            # Verify download
            data_file = os.path.join(miner_data_dir, "data.jsonl")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    lines = len(f.readlines())
                bt.logging.success(f"UID {uid}: Downloaded {lines} data entries from {metadata.id.namespace}")
                downloaded.append((uid, metadata.id.namespace, metadata.id.commit, lines))
            else:
                bt.logging.error(f"UID {uid}: Downloaded but data.jsonl not found")
                failed.append((uid, "Data file not found"))
                
        except Exception as e:
            bt.logging.error(f"UID {uid}: Failed to download dataset: {e}")
            failed.append((uid, str(e)))
    
    # Summary
    bt.logging.info("=" * 80)
    bt.logging.info("DOWNLOAD SUMMARY")
    bt.logging.info("=" * 80)
    bt.logging.info(f"Target coldkey: {target_coldkey}")
    bt.logging.info(f"Found miners: {matching_uids}")
    bt.logging.info(f"Successfully downloaded: {len(downloaded)}")
    bt.logging.info(f"Failed: {len(failed)}")
    
    if downloaded:
        bt.logging.info("\nDownloaded miners:")
        for uid, namespace, commit, lines in downloaded:
            bt.logging.info(f"  UID {uid}: {namespace}@{commit[:8]} ({lines} entries)")
    
    if failed:
        bt.logging.info("\nFailed miners:")
        for uid, reason in failed:
            bt.logging.info(f"  UID {uid}: {reason}")
    
    bt.logging.info("=" * 80)
    
    return matching_uids


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 find_miners_by_coldkey.py <coldkey> [--netuid <netuid>]")
        sys.exit(1)
    
    target_coldkey = sys.argv[1]
    find_and_download_by_coldkey(target_coldkey)

