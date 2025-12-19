#!/bin/bash
# Local test script to simulate GitHub Actions workflow

set -e

echo "=========================================="
echo "Testing GitHub Actions Workflow Locally"
echo "=========================================="

# Check if .secrets file exists
if [ ! -f .secrets ]; then
    echo "Error: .secrets file not found"
    echo "Create .secrets file with:"
    echo "  EDDI_SERIAL_NUMBER=your_serial"
    echo "  EDDI_API_KEY=your_key"
    echo "  EDDI_BASE_URL=https://s18.myenergi.net"
    exit 1
fi

# Load secrets
echo "Loading secrets from .secrets file..."
set -a
source .secrets
set +a

# Validate required secrets are set
if [ -z "$EDDI_SERIAL_NUMBER" ] || [ -z "$EDDI_API_KEY" ]; then
    echo "Error: Required environment variables not set"
    echo "Make sure .secrets contains:"
    echo "  EDDI_SERIAL_NUMBER=your_serial"
    echo "  EDDI_API_KEY=your_key"
    exit 1
fi

# Check command argument
COMMAND=${1:-stop}

if [ "$COMMAND" != "stop" ] && [ "$COMMAND" != "start" ]; then
    echo "Usage: $0 [stop|start]"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test: Manual trigger with command=$COMMAND"
echo "=========================================="

# Run the helper script
pixi run python scripts/eddi_control.py \
    "$COMMAND" \
    --serial "$EDDI_SERIAL_NUMBER" \
    --api-key "$EDDI_API_KEY" \
    --base-url "${EDDI_BASE_URL:-https://s18.myenergi.net}" \
    --max-retries 3

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Workflow test PASSED"
else
    echo "✗ Workflow test FAILED"
fi
echo "=========================================="

exit $EXIT_CODE
