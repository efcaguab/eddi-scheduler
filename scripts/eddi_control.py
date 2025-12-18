#!/usr/bin/env python3
"""
GitHub Actions helper script to control eddi device with retry and verification.
"""

import sys
import time
import argparse
from pathlib import Path

# Add parent directory to path to import eddi_scheduler
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eddi_scheduler.client import EddiClient


def wait_and_verify_stop(client, device_serial, max_attempts=10, wait_between=15):
    """
    Verify that device has stopped (sta=6).
    Device transitions: sta=3 (diverting) -> sta=1 (paused) -> sta=6 (stopped)
    This can take up to 2-3 minutes.
    
    Args:
        client: EddiClient instance
        device_serial: Device serial number
        max_attempts: Maximum number of verification attempts
        wait_between: Seconds to wait between attempts
    
    Returns:
        bool: True if stopped (sta=6), False otherwise
    """
    print(f"Verifying device stopped (expecting sta=6)...")
    print(f"Note: Device may go through sta=1 (paused) before reaching sta=6 (stopped)")
    
    for attempt in range(1, max_attempts + 1):
        time.sleep(wait_between)
        
        try:
            devices = client.get_eddi_devices()
            device = next((d for d in devices if str(d.get("sno")) == device_serial), None)
            
            if not device:
                print(f"  Attempt {attempt}/{max_attempts}: Device not found")
                continue
            
            sta = device.get("sta")
            div = device.get("div", 0)
            
            print(f"  Attempt {attempt}/{max_attempts}: sta={sta}, div={div}W")
            
            if sta == 6:
                print(f"✓ Device stopped successfully (sta=6)")
                return True
            elif sta == 1:
                print(f"  → Device in paused state (sta=1), continuing to wait for sta=6...")
            
        except Exception as e:
            print(f"  Attempt {attempt}/{max_attempts}: Error checking status: {e}")
    
    print(f"✗ Device did not reach stopped state (sta=6) after {max_attempts} attempts")
    return False


def wait_and_verify_start(client, device_serial, max_attempts=5, wait_between=10):
    """
    Verify that device has started (sta=3 for diverting).
    
    Args:
        client: EddiClient instance
        device_serial: Device serial number
        max_attempts: Maximum number of verification attempts
        wait_between: Seconds to wait between attempts
    
    Returns:
        bool: True if started (sta=3), False otherwise
    """
    print(f"Verifying device started (expecting sta=3 for diverting)...")
    
    for attempt in range(1, max_attempts + 1):
        time.sleep(wait_between)
        
        try:
            devices = client.get_eddi_devices()
            device = next((d for d in devices if str(d.get("sno")) == device_serial), None)
            
            if not device:
                print(f"  Attempt {attempt}/{max_attempts}: Device not found")
                continue
            
            sta = device.get("sta")
            div = device.get("div", 0)
            
            print(f"  Attempt {attempt}/{max_attempts}: sta={sta}, div={div}W")
            
            if sta == 3:
                print(f"✓ Device started and diverting (sta=3, {div}W)")
                return True
            elif sta == 1 and attempt == max_attempts:
                print(f"⚠ Device in paused state (sta=1), may be waiting for surplus power")
                # Consider this partial success - device is in normal mode, just no power to divert
                return True
                
        except Exception as e:
            print(f"  Attempt {attempt}/{max_attempts}: Error checking status: {e}")
    
    print(f"✗ Device did not reach started state after {max_attempts} attempts")
    return False


def execute_command_with_retry(command, client, device_serial, max_retries=3):
    """
    Execute stop/start command with retry logic.
    
    Args:
        command: "stop" or "start"
        client: EddiClient instance
        device_serial: Device serial number
        max_retries: Maximum number of retry attempts
    
    Returns:
        bool: True if command succeeded and verified, False otherwise
    """
    for retry in range(1, max_retries + 1):
        print(f"\n{'='*60}")
        print(f"Attempt {retry}/{max_retries}: Executing {command.upper()} command")
        print(f"{'='*60}")
        
        try:
            # Execute command
            if command == "stop":
                result = client.stop(device_serial)
            elif command == "start":
                result = client.start(device_serial)
            else:
                print(f"✗ Unknown command: {command}")
                return False
            
            print(f"Command sent: {result}")
            
            # Wait initial period for command to take effect
            if command == "stop":
                print(f"Waiting 30 seconds for stop command to take effect...")
                time.sleep(30)
                # Stop can take 2-3 minutes: sta=3 -> sta=1 -> sta=6
                if wait_and_verify_stop(client, device_serial, max_attempts=10, wait_between=15):
                    return True
            else:  # start
                print(f"Waiting 50 seconds for start command to take effect...")
                time.sleep(50)
                if wait_and_verify_start(client, device_serial):
                    return True
            
            if retry < max_retries:
                print(f"\nRetrying in 30 seconds...")
                time.sleep(30)
                
        except Exception as e:
            print(f"✗ Error executing command: {e}")
            if retry < max_retries:
                print(f"\nRetrying in 30 seconds...")
                time.sleep(30)
    
    print(f"\n✗ Command failed after {max_retries} attempts")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Control eddi device with verification and retry"
    )
    parser.add_argument(
        "command",
        choices=["stop", "start"],
        help="Command to execute"
    )
    parser.add_argument(
        "--serial",
        required=True,
        help="Device serial number"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="API key"
    )
    parser.add_argument(
        "--base-url",
        default="https://s18.myenergi.net",
        help="API base URL"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Eddi Control Script")
    print(f"{'='*60}")
    print(f"Command: {args.command.upper()}")
    print(f"Device: {args.serial}")
    print(f"Base URL: {args.base_url}")
    print(f"Max Retries: {args.max_retries}")
    print(f"{'='*60}\n")
    
    # Create client
    client = EddiClient(args.serial, args.api_key, args.base_url)
    
    # Execute command with retry
    success = execute_command_with_retry(
        args.command,
        client,
        args.serial,
        args.max_retries
    )
    
    # Exit with appropriate code
    if success:
        print(f"\n{'='*60}")
        print(f"✓ SUCCESS: {args.command.upper()} command completed")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print(f"✗ FAILURE: {args.command.upper()} command failed")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
