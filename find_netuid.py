#!/usr/bin/env python3
"""
Quick script to find the netuid for FLock subnet by searching all subnets.
"""

import bittensor as bt

def find_flock_netuid():
    """Find the netuid for FLock subnet."""
    config = bt.config()
    
    print("Connecting to Bittensor network...")
    subtensor = bt.subtensor(config=config)
    
    print(f"Connected to: {subtensor.network}")
    print("\nFetching all subnets...")
    
    subnets = subtensor.get_subnets()
    print(f"Found {len(subnets)} subnets")
    
    print("\nSearching for FLock subnet...")
    for netuid in subnets:
        try:
            metagraph = subtensor.metagraph(netuid)
            print(f"\nNetUID {netuid}:")
            print(f"  Total miners: {len(metagraph.uids)}")
            print(f"  Hotkeys: {metagraph.hotkeys[:5] if len(metagraph.hotkeys) >= 5 else metagraph.hotkeys}")
        except Exception as e:
            print(f"\nNetUID {netuid}: Error - {e}")

if __name__ == "__main__":
    find_flock_netuid()

