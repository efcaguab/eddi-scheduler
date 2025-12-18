# Automated Scheduler

This repository includes a GitHub Actions workflow that automatically controls the eddi device based on a schedule.

## Schedule (New Zealand Time)

| Day | Time | Action |
|-----|------|--------|
| Monday-Friday | 10:00 AM | **START** (begin diverting) |
| Monday-Friday | 5:00 PM | **STOP** (pause diverting) |
| Saturday | 5:00 AM | **START** (begin diverting) |
| Sunday | 10:00 PM | **STOP** (pause diverting) |

## How It Works

1. **Hourly Check**: GitHub Actions runs every hour
2. **NZ Time Calculation**: Checks current time in Pacific/Auckland timezone (handles DST automatically)
3. **Command Execution**: If it's a scheduled time, executes the appropriate command
4. **Verification**: Waits and verifies the command succeeded by checking device status
5. **Retry Logic**: Automatically retries up to 3 times if command fails

## Success Criteria

- **STOP Command**: Device must reach `sta=6` (Stopped)
- **START Command**: Device must reach `sta=3` (Diverting) or `sta=1` (Paused, waiting for surplus power)

## Setup

### 1. Add GitHub Secrets

In your repository settings, add these secrets:

- `EDDI_SERIAL_NUMBER`: Your hub serial number
- `EDDI_API_KEY`: Your myenergi API key
- `EDDI_BASE_URL`: (Optional) Default is `https://s18.myenergi.net`

### 2. Enable GitHub Actions

The workflow is in `.github/workflows/eddi-scheduler.yml` and will run automatically once secrets are configured.

### 3. Manual Testing

You can manually trigger the workflow:

1. Go to Actions tab in GitHub
2. Select "Eddi Scheduler" workflow
3. Click "Run workflow"
4. Choose "start" or "stop" command
5. Click "Run workflow" button

## Monitoring

- Check the **Actions** tab in GitHub to see workflow runs
- Each run shows detailed logs including:
  - Current NZ time
  - Command execution
  - Status verification attempts
  - Success/failure status

## Troubleshooting

**Workflow not running?**
- Check that secrets are added correctly
- Verify GitHub Actions is enabled for your repository

**Commands failing?**
- Check workflow logs for error messages
- Verify device is online and accessible
- Check API credentials are correct

**Wrong timezone?**
- The workflow automatically handles NZ daylight saving time
- Logs show the detected NZ time for verification

## Technical Details

- **Helper Script**: `scripts/eddi_control.py`
- **Workflow**: `.github/workflows/eddi-scheduler.yml`
- **Timezone**: `Pacific/Auckland` (UTC+12/+13 with DST)
- **Schedule Window**: ±30 minutes (commands execute within 30 minutes of scheduled time)
- **Max Retries**: 3 attempts with 30-second delays
- **Verification Interval**: Checks status every 10 seconds, up to 5 times
