"""Command-line interface for eddi-scheduler."""

import sys
from typing import Optional
import click
from .client import EddiClient


@click.group()
@click.option(
    "--serial",
    envvar="EDDI_SERIAL_NUMBER",
    required=True,
    help="Hub serial number (or set EDDI_SERIAL_NUMBER env var)"
)
@click.option(
    "--api-key",
    envvar="EDDI_API_KEY",
    required=True,
    help="API key/password (or set EDDI_API_KEY env var)"
)
@click.option(
    "--base-url",
    envvar="EDDI_BASE_URL",
    default="https://s18.myenergi.net",
    help="Base URL for API (default: https://s18.myenergi.net)"
)
@click.pass_context
def cli(ctx, serial: str, api_key: str, base_url: str):
    """Control myenergi eddi device modes.

    Set EDDI_SERIAL_NUMBER and EDDI_API_KEY environment variables
    to avoid passing credentials on command line.
    """
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
            status_code = eddi.get("sta", "unknown")
            temp1 = eddi.get("tp1", "N/A")
            temp2 = eddi.get("tp2", "N/A")
            heater_name1 = eddi.get("ht1", "Heater 1")
            heater_name2 = eddi.get("ht2", "Heater 2")
            
            click.echo(f"\nEddi Device: {serial}")
            click.echo(f"  Status: {status_code}")
            click.echo(f"  {heater_name1} Temp: {temp1}°C")
            click.echo(f"  {heater_name2} Temp: {temp2}°C")
            
    except Exception as e:
        click.echo(f"Error getting status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
@click.argument("device", required=False)
def stop(ctx, device: Optional[str]):
    """Put eddi device into stop mode.

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
            click.echo(f"✓ Eddi device {device} set to STOP mode")
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
    """Put eddi device into normal mode (exit stop mode).

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
            click.echo(f"✓ Eddi device {device} set to NORMAL mode")
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
