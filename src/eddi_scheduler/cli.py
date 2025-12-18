"""Command-line interface for eddi-scheduler."""

import sys
import json
from pathlib import Path
from typing import Optional
import click
from dotenv import load_dotenv
from .client import EddiClient

# Status code meanings
STATUS_CODES = {
    1: "Paused",
    3: "Diverting",
    4: "Boosting",
    5: "Max Temp Reached",
    6: "Stopped"
}

# Load .env file if it exists in current working directory
# Note: The .env file must be in the directory where you run the command
env_path = Path.cwd() / '.env'
if env_path.exists():
    load_dotenv(env_path)


@click.group()
@click.option(
    "--serial",
    envvar="EDDI_SERIAL_NUMBER",
    help="Hub serial number (or set EDDI_SERIAL_NUMBER env var or use .env file)"
)
@click.option(
    "--api-key",
    envvar="EDDI_API_KEY",
    help="API key/password (or set EDDI_API_KEY env var or use .env file)"
)
@click.option(
    "--base-url",
    envvar="EDDI_BASE_URL",
    default="https://s18.myenergi.net",
    help="Base URL for API (default: https://s18.myenergi.net, or set via .env file)"
)
@click.pass_context
def cli(ctx, serial: str, api_key: str, base_url: str):
    """Control myenergi eddi device modes.
    
    Credentials can be provided via:
    1. .env file in current directory
    2. Environment variables (EDDI_SERIAL_NUMBER, EDDI_API_KEY, EDDI_BASE_URL)
    3. Command line options (--serial, --api-key, --base-url)

    Set EDDI_SERIAL_NUMBER and EDDI_API_KEY environment variables
    to avoid passing credentials on command line.
    """
    # Validate that required credentials are provided
    if not serial:
        click.echo("Error: Missing --serial option or EDDI_SERIAL_NUMBER environment variable", err=True)
        click.echo("Tip: Create a .env file in the current directory with EDDI_SERIAL_NUMBER=your_serial", err=True)
        sys.exit(1)
    
    if not api_key:
        click.echo("Error: Missing --api-key option or EDDI_API_KEY environment variable", err=True)
        click.echo("Tip: Create a .env file in the current directory with EDDI_API_KEY=your_key", err=True)
        sys.exit(1)
    
    ctx.ensure_object(dict)
    ctx.obj["client"] = EddiClient(serial, api_key, base_url)


@cli.command()
@click.pass_context
@click.option(
    "--device",
    help="Specific eddi serial number (if multiple devices)"
)
def status(ctx, device: Optional[str]):
    """Show status of eddi device(s)."""
    client: EddiClient = ctx.obj["client"]
    
    try:
        devices = client.get_eddi_devices()
        
        if not devices:
            click.echo("No eddi devices found.")
            sys.exit(1)
        
        if device:
            devices = [d for d in devices if str(d.get("sno")) == device]
            if not devices:
                click.echo(f"No eddi device found with serial: {device}")
                sys.exit(1)
        
        for eddi in devices:
            serial = eddi.get("sno")
            sta = eddi.get("sta", 0)
            status_text = STATUS_CODES.get(sta, f"Unknown ({sta})")
            div = eddi.get("div", 0)
            grd = eddi.get("grd", 0)
            temp1 = eddi.get("tp1", -1)
            temp2 = eddi.get("tp2", -1)
            heater1 = eddi.get("ht1", "Heater 1")
            heater2 = eddi.get("ht2", "Heater 2")
            
            click.echo(f"\n=== Eddi Device {serial} ===")
            click.echo(f"Status: {status_text} (sta={sta})")
            click.echo(f"Diverting: {div}W")
            click.echo(f"Grid: {grd}W (negative = exporting)")
            click.echo(f"{heater1}: {temp1}°C")
            click.echo(f"{heater2}: {temp2}°C")
            click.echo(f"\nFull device data:")
            click.echo(json.dumps(eddi, indent=2))
            
    except Exception as e:
        click.echo(f"Error getting status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
@click.argument("device", required=False)
def stop(ctx, device: Optional[str]):
    """Put eddi device into stop mode (pause diverting).

    This will stop the eddi from diverting power to the heater.
    The device will transition from Diverting (sta=3) to Paused (sta=1).
    This typically takes 5-10 seconds to take effect.

    If DEVICE serial number is not provided, will use the first eddi device found.
    """
    client: EddiClient = ctx.obj["client"]
    
    try:
        # Get device serial if not provided
        if not device:
            devices = client.get_eddi_devices()
            if not devices:
                click.echo("No eddi devices found.")
                sys.exit(1)
            device = str(devices[0].get("sno"))
            click.echo(f"Using eddi device: {device}")
        
        # Set to stop mode
        result = client.stop(device)
        
        if result.get("status") == 0:
            click.echo(f"✓ Stop command sent to eddi device {device}")
            click.echo("  Device will stop diverting within 5-10 seconds")
            click.echo("  Use 'status' command to verify")
        else:
            click.echo(
                f"Warning: Unexpected response: {result.get('statustext', 'unknown')}",
                err=True
            )
            
    except Exception as e:
        click.echo(f"Error setting stop mode: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
@click.argument("device", required=False)
def start(ctx, device: Optional[str]):
    """Put eddi device into normal mode (resume diverting).

    This will allow the eddi to resume diverting excess power to the heater.
    The device will transition through: Stopped (sta=6) → Paused (sta=1) → Diverting (sta=3)
    This typically takes 40-50 seconds to fully resume diverting (if power is available).

    If DEVICE serial number is not provided, will use the first eddi device found.
    """
    client: EddiClient = ctx.obj["client"]
    
    try:
        # Get device serial if not provided
        if not device:
            devices = client.get_eddi_devices()
            if not devices:
                click.echo("No eddi devices found.")
                sys.exit(1)
            device = str(devices[0].get("sno"))
            click.echo(f"Using eddi device: {device}")
        
        # Set to normal mode
        result = client.start(device)
        
        if result.get("status") == 0:
            click.echo(f"✓ Start command sent to eddi device {device}")
            click.echo("  Device will resume normal operation within 40-50 seconds")
            click.echo("  Use 'status' command to verify when it starts diverting")
        else:
            click.echo(
                f"Warning: Unexpected response: {result.get('statustext', 'unknown')}",
                err=True
            )
            
    except Exception as e:
        click.echo(f"Error setting normal mode: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
