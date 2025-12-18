# Quick Reference Card

## Your Credentials
```bash
Hub Serial: E23510540
API Key: CCMcv8sDwDLfkiaCuJojzEPo
```

## One-Time Setup
```bash
# Install
pip install -e .

# Set environment variables (add to ~/.bashrc or ~/.zshrc)
export EDDI_SERIAL_NUMBER="E23510540"
export EDDI_API_KEY="CCMcv8sDwDLfkiaCuJojzEPo"
```

## Daily Commands

### Check Status
```bash
eddi status
```

### Stop Mode (turn off)
```bash
eddi stop
```

### Normal Mode (turn on)
```bash
eddi start
```

## Without Environment Variables
If you haven't set up environment variables, use the full command:

```bash
eddi --serial E23510540 --api-key CCMcv8sDwDLfkiaCuJojzEPo <command>
```

## Automation Examples

### Using Cron (scheduled tasks)
```bash
# Edit crontab
crontab -e

# Stop at 11 PM, start at 7 AM
0 23 * * * eddi stop
0 7 * * * eddi start
```

### Using Shell Script
```bash
#!/bin/bash
# Save as ~/eddi-control.sh

case "$1" in
    on)   eddi start ;;
    off)  eddi stop ;;
    info) eddi status ;;
    *)    echo "Usage: $0 {on|off|info}" ;;
esac
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing option '--serial'" | Set environment variables or use `--serial` and `--api-key` options |
| "No eddi devices found" | Check your credentials and internet connection |
| Command not found | Run `pip install -e .` in the project directory |

## Help
```bash
eddi --help           # General help
eddi status --help    # Command-specific help
```
