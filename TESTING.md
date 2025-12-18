# Testing GitHub Actions Workflow

## Manual Testing on GitHub

1. **Go to your repository on GitHub**
   - Navigate to: https://github.com/efcaguab/eddi-scheduler

2. **Switch to the feature branch**
   - Click on the branch selector (shows "main")
   - Select: `feature/github-actions-scheduler`

3. **Go to Actions tab**
   - Click "Actions" at the top

4. **Find the workflow**
   - Look for "Eddi Scheduler" in the left sidebar
   - Click on it

5. **Run workflow manually**
   - Click "Run workflow" button (top right)
   - Keep branch as `feature/github-actions-scheduler`
   - Choose command: `stop` or `start`
   - Click green "Run workflow" button

6. **Watch the execution**
   - Click on the running workflow
   - Click on the job name to see logs
   - Check each step for output

## What to Check

### Stop Command Test
- Command should be sent
- Status should be verified
- **Expected**: Device reaches `sta=6` OR `sta=1` (need clarification)

### Start Command Test  
- Command should be sent
- Status should be verified
- **Expected**: Device reaches `sta=3` (diverting) OR `sta=1` (waiting for power)

## Current Issue: Stop State Clarification Needed

From testing, we observe:
- **sta=1**: Paused (what we get from API stop command)
- **sta=6**: Stopped (different state)

### Questions:
1. When you manually press "Stop" on the physical eddi device, what `sta` code shows up?
2. Is `sta=1` (Paused, not diverting) acceptable for the scheduler?
3. Do we need to achieve `sta=6` specifically? If so, how?

## Local Testing (Alternative)

If GitHub Actions has issues, test locally:

```bash
# Test stop command
pixi run python scripts/eddi_control.py stop \
  --serial 23510540 \
  --api-key "YOUR_KEY" \
  --base-url "https://s18.myenergi.net" \
  --max-retries 1

# Test start command
pixi run python scripts/eddi_control.py start \
  --serial 23510540 \
  --api-key "YOUR_KEY" \
  --base-url "https://s18.myenergi.net" \
  --max-retries 1
```

## Status Codes Reference

| Code | Status | Meaning |
|------|--------|---------|
| 1 | Paused | Not diverting (result of API stop) |
| 3 | Diverting | Actively heating |
| 6 | Stopped | Different stopped state |

## Next Steps

1. **Clarify** sta=6 vs sta=1 requirement
2. **Test** workflow on GitHub manually
3. **Adjust** script if needed based on test results
4. **Monitor** first scheduled run
