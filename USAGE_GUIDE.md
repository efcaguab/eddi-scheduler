# Quick Start Guide

This guide will help you get started with controlling your eddi device.

## Installation

```bash
# From the repository directory
pip install -e .
```

## Setup Your Credentials

You have two options for providing credentials:

### Option 1: Environment Variables (Recommended)

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
export EDDI_SERIAL_NUMBER="E23510540"
export EDDI_API_KEY="CCMcv8sDwDLfkiaCuJojzEPo"
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Option 2: Command Line Options

Pass credentials with each command:

```bash
eddi --serial E23510540 --api-key CCMcv8sDwDLfkiaCuJojzEPo <command>
```

## Usage Examples

### Check the status of your eddi

```bash
# With environment variables set:
eddi status

# Or with command line options:
eddi --serial E23510540 --api-key CCMcv8sDwDLfkiaCuJojzEPo status
```

This will show you:
- Device serial number
- Current status code
- Temperature readings
- Heater names and states

### Put your eddi into STOP mode

```bash
# With environment variables:
eddi stop

# With command line options:
eddi --serial E23510540 --api-key CCMcv8sDwDLfkiaCuJojzEPo stop
```

When successful, you'll see:
```
✓ Eddi device 23510540 set to STOP mode
```

### Return your eddi to NORMAL mode

```bash
# With environment variables:
eddi start

# With command line options:
eddi --serial E23510540 --api-key CCMcv8sDwDLfkiaCuJojzEPo start
```

When successful, you'll see:
```
✓ Eddi device 23510540 set to NORMAL mode
```

## Automating with Cron or Scripts

You can automate the eddi control using cron jobs or shell scripts.

### Example: Stop eddi at 11 PM, start at 7 AM

Edit your crontab:
```bash
crontab -e
```

Add these lines:
```cron
# Stop eddi at 11 PM every day
0 23 * * * /usr/local/bin/eddi stop

# Start eddi at 7 AM every day  
0 7 * * * /usr/local/bin/eddi start
```

Make sure your environment variables are set in your cron environment, or use the full command with credentials.

### Example: Shell script for manual control

Create a file `~/control-eddi.sh`:

```bash
#!/bin/bash

case "$1" in
    stop)
        echo "Stopping eddi..."
        eddi stop
        ;;
    start)
        echo "Starting eddi..."
        eddi start
        ;;
    status)
        echo "Checking eddi status..."
        eddi status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
```

Make it executable:
```bash
chmod +x ~/control-eddi.sh
```

Use it:
```bash
~/control-eddi.sh stop
~/control-eddi.sh start
~/control-eddi.sh status
```

## Troubleshooting

### "No eddi devices found"

- Check your credentials are correct
- Verify your hub serial number (E23510540)
- Ensure your API key is valid

### "Error getting status: Connection error"

- Check your internet connection
- Verify the myenergi service is available
- You may need to use a different base URL (check myenergi documentation)

### "Invalid mode"

This error shouldn't occur with the commands, but if you're using the Python API directly, ensure you're using 'stop' or 'normal' as mode values.

## Getting Help

```bash
# General help
eddi --help

# Help for specific commands
eddi status --help
eddi stop --help
eddi start --help
```

## Security Notes

- Never commit your API key to version control
- Keep your `.env` file in `.gitignore` (already configured)
- Use environment variables instead of command line options when possible (command line args can be visible in process lists)
- The API key is stored in myenergi's secure system and uses digest authentication
