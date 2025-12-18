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

### 3. Testing

#### Local Testing (Recommended First)

Test the workflow locally before deploying:

```bash
# Test stop command
./test_workflow.sh stop

# Test start command
./test_workflow.sh start
```

This requires a `.secrets` file in the project directory with your credentials (see TESTING.md).

#### GitHub Actions Testing

Once merged to main, you can manually trigger the workflow:

1. Go to Actions tab in GitHub
2. Select "Eddi Scheduler" workflow
3. Click "Run workflow"
4. Choose "start" or "stop" command
5. Click "Run workflow" button

**Note**: GitHub Actions workflows only appear in the Actions tab after the branch is merged to main.

## Monitoring

- Check the **Actions** tab in GitHub to see workflow runs
- Each run shows detailed logs including:
  - Current NZ time
  - Command execution
  - Status verification attempts
  - Success/failure status

## Troubleshooting

**Local testing failing?**
- Ensure `.secrets` file exists with correct credentials
- Check device is online: `pixi run python -m eddi_scheduler.cli status`
- Run with verbose output: `pixi run python scripts/eddi_control.py stop --serial ... --api-key ... --base-url ...`

**Workflow not running?**
- Workflows only appear after merging to main branch
- Check that secrets are added correctly in GitHub repository settings
- Verify GitHub Actions is enabled for your repository

**Commands failing?**
- Check workflow logs for error messages
- Verify device is online and accessible
- Check API credentials are correct
- Stop command needs ~3 minutes to reach sta=6
- Start command may stay at sta=1 if no surplus power available

**Wrong timezone?**
- The workflow automatically handles NZ daylight saving time (Pacific/Auckland)
- Logs show the detected NZ time for verification
- Test timezone logic: `pixi run python -c "import pytz; from datetime import datetime; print(datetime.now(pytz.timezone('Pacific/Auckland')))"`

## Technical Details

- **Helper Script**: `scripts/eddi_control.py`
- **Workflow**: `.github/workflows/eddi-scheduler.yml`
- **Local Test Script**: `test_workflow.sh`
- **Timezone**: `Pacific/Auckland` (UTC+12/+13 with DST)
- **Schedule Window**: ±30 minutes (commands execute within 30 minutes of scheduled time)
- **Max Retries**: 3 attempts with 30-second delays
- **Stop Verification**: 
  - Initial wait: 30 seconds
  - Checks every 15 seconds, up to 10 times (~2.5 minutes total)
  - Success: sta=6 (Stopped)
- **Start Verification**: 
  - Initial wait: 50 seconds
  - Checks every 10 seconds, up to 5 times
  - Success: sta=3 (Diverting) or sta=1 (Paused, waiting for surplus power)
