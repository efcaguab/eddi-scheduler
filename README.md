# eddi-scheduler

CLI tool to remotely control myenergi eddi devices - stop and start diverting on demand.

## Quick Start

```bash
# 1. Install
git clone https://github.com/efcaguab/eddi-scheduler.git
cd eddi-scheduler
pixi install

# 2. Configure - create .env file
cat > .env << EOF
EDDI_SERIAL_NUMBER=your_hub_serial
EDDI_API_KEY=your_api_key
EDDI_BASE_URL=https://s18.myenergi.net
EOF

# 3. Use
pixi run python -m eddi_scheduler.cli status
pixi run python -m eddi_scheduler.cli stop
pixi run python -m eddi_scheduler.cli start
```

**Optional**: Create an alias for convenience:
```bash
alias eddi='cd /path/to/eddi-scheduler && pixi run python -m eddi_scheduler.cli'
```

## Commands

| Command | Action | Time to take effect |
|---------|--------|---------------------|
| `status` | Show device status and power diversion | Instant |
| `stop` | Pause power diversion | ~5-10 seconds |
| `start` | Resume power diversion | ~40-50 seconds |

## Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 1 | Paused | Waiting for surplus power |
| 3 | Diverting | Actively heating |
| 6 | Stopped | Won't divert (manual stop) |

## Getting API Credentials

Get your hub serial number and API key from myenergi: https://support.myenergi.com/hc/en-gb/articles/4404522743313-myenergi-API

## Troubleshooting

**Commands don't work?**
- Make sure you're in the project directory (where .env file is)
- Wait 10-50 seconds after sending command before checking status
- Check that there's excess solar power available (negative grid value)

**"No eddi devices found"?**
- Verify credentials in .env file are correct
- Try base URL https://s11.myenergi.net instead

## Development

```bash
pixi install              # Install dependencies
pixi run pytest           # Run tests
```

## License

MIT License - Unofficial tool, not affiliated with myenergi. Use at your own risk.
