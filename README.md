# eddi-scheduler

A command-line interface (CLI) tool to control myenergi eddi devices. This tool allows you to remotely put your eddi device into stop mode or return it to normal operation on demand.

## Features

- 🛑 **Stop Mode**: Put your eddi into stop mode on command
- ▶️ **Normal Mode**: Exit stop mode and return to normal operation
- 📊 **Status Check**: View current status of your eddi device(s)
- 🔐 **Secure**: Uses myenergi's official API with digest authentication
- 🚀 **Simple**: Easy-to-use CLI with sensible defaults

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/efcaguab/eddi-scheduler.git
cd eddi-scheduler

# Install in development mode
pip install -e .
```

### Using pip (once published)

```bash
pip install eddi-scheduler
```

## Prerequisites

You need:
1. A myenergi eddi device
2. Your hub serial number
3. An API key from myenergi

To obtain an API key, follow the instructions here: https://support.myenergi.com/hc/en-gb/articles/4404522743313-myenergi-API

## Configuration

Set up your credentials using environment variables:

```bash
export EDDI_SERIAL_NUMBER="your_hub_serial"
export EDDI_API_KEY="your_api_key"
```

You can also add these to your `~/.bashrc` or `~/.zshrc` file to make them permanent.

Alternatively, you can pass credentials as command-line options (see Usage below).

## Usage

### Check status

View the current status of your eddi device(s):

```bash
eddi status
```

### Put eddi into stop mode

```bash
eddi stop
```

If you have multiple eddi devices, specify the device serial number:

```bash
eddi stop 10088888
```

### Return eddi to normal mode

```bash
eddi start
```

Or for a specific device:

```bash
eddi start 10088888
```

### Passing credentials as options

If you prefer not to use environment variables:

```bash
eddi --serial YOUR_SERIAL --api-key YOUR_API_KEY status
eddi --serial YOUR_SERIAL --api-key YOUR_API_KEY stop
eddi --serial YOUR_SERIAL --api-key YOUR_API_KEY start
```

### Help

Get help for any command:

```bash
eddi --help
eddi status --help
eddi stop --help
eddi start --help
```

## API Reference

The tool uses the myenergi API endpoints:
- `/cgi-jstatus-*` - Get device status
- `/cgi-eddi-mode-E<serial>-0` - Set to stop mode
- `/cgi-eddi-mode-E<serial>-1` - Set to normal mode

## Development

### Setting up development environment

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Thanks to the myenergi community for reverse-engineering the API
- Special thanks to [twonk/MyEnergi-App-Api](https://github.com/twonk/MyEnergi-App-Api) for API documentation
- Inspired by [skywatcher-uk/myenergi](https://github.com/skywatcher-uk/myenergi) Python library

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by myenergi. Use at your own risk.
