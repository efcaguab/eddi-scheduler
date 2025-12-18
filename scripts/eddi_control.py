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

# Constants for timing and verification
STOP_MAX_ATTEMPTS = 10
STOP_WAIT_BETWEEN = 15  # seconds
STOP_INITIAL_WAIT = 30  # seconds

START_MAX_ATTEMPTS = 5
START_WAIT_BETWEEN = 10  # seconds
START_INITIAL_WAIT = 50  # seconds

MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds


def wait_and_verify_stop(client, device_serial, max_attempts=STOP_MAX_ATTEMPTS, wait_between=STOP_WAIT_BETWEEN):
    """
    Verify that device has stopped (sta=6) - ONLY sta=6 is acceptable.
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
    print(f"Verifying device stopped (expecting sta=6 ONLY)...")
    print(f"Note: Device may go through sta=1 (paused) before reaching sta=6 (stopped)")
    
    device_not_found_count = 0
    
    for attempt in range(1, max_attempts + 1):
        time.sleep(wait_between)
        
        try:
            devices = client.get_eddi_devices()
            device = next((d for d in devices if str(d.get("sno")) == device_serial), None)
            
            if not device:
                device_not_found_count += 1
                print(f"  Attempt {attempt}/{max_attempts}: Device not found")
                if device_not_found_count >= 3:
                    print(f"✗ Device not found in 3+ consecutive attempts - check network/credentials")
                    return False
                continue
            
            # Reset counter if device is found
            device_not_found_count = 0
            
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


def wait_and_verify_start(client, device_serial, max_attempts=START_MAX_ATTEMPTS, wait_between=START_WAIT_BETWEEN):
    """
    Verify that device has started (any status except sta=6 stopped).
    Success means sta != 6 (can be 1, 3, or other codes, but NOT 6).
    
    Args:
        client: EddiClient instance
        device_serial: Device serial number
        max_attempts: Maximum number of verification attempts
        wait_between: Seconds to wait between attempts
    
    Returns:
        bool: True if started (sta != 6), False otherwise
    """
    print(f"Verifying device started (expecting any status EXCEPT sta=6 stopped)...")
    
    # Status code descriptions for common states
    status_descriptions = {
        1: "paused/waiting for surplus power",
        3: "actively diverting power"
    }
    
    device_not_found_count = 0
    
    for attempt in range(1, max_attempts + 1):
        time.sleep(wait_between)
        
        try:
            devices = client.get_eddi_devices()
            device = next((d for d in devices if str(d.get("sno")) == device_serial), None)
            
            if not device:
                device_not_found_count += 1
                print(f"  Attempt {attempt}/{max_attempts}: Device not found")
                if device_not_found_count >= 3:
                    print(f"✗ Device not found in 3+ consecutive attempts - check network/credentials")
                    return False
                continue
            
            # Reset counter if device is found
            device_not_found_count = 0
            
            sta = device.get("sta")
            div = device.get("div", 0)
            
            print(f"  Attempt {attempt}/{max_attempts}: sta={sta}, div={div}W")
            
            if sta is None:
                print(f"  → Device status unavailable, retrying...")
                continue
            elif sta == 6:
                print(f"  → Device still stopped (sta=6), waiting for start...")
                continue
            else:
                # Any status except 6 (and not None) means the device has started successfully
                description = status_descriptions.get(sta, f"running (code {sta})")
                print(f"✓ Device started successfully (sta={sta}, {description}, {div}W)")
                return True
                
        except Exception as e:
            print(f"  Attempt {attempt}/{max_attempts}: Error checking status: {e}")
    
    print(f"✗ Device did not reach started state after {max_attempts} attempts")
    return False


def execute_command_with_retry(command, client, device_serial, max_retries=MAX_RETRIES):
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
                print(f"Waiting {STOP_INITIAL_WAIT} seconds for stop command to take effect...")
                time.sleep(STOP_INITIAL_WAIT)
                # Stop can take 2-3 minutes: sta=3 -> sta=1 -> sta=6
                if wait_and_verify_stop(client, device_serial):
                    return True
            else:  # start
                print(f"Waiting {START_INITIAL_WAIT} seconds for start command to take effect...")
                time.sleep(START_INITIAL_WAIT)
                if wait_and_verify_start(client, device_serial):
                    return True
            
            if retry < max_retries:
                print(f"\nRetrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                
        except Exception as e:
            print(f"✗ Error executing command: {e}")
            if retry < max_retries:
                print(f"\nRetrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    
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
