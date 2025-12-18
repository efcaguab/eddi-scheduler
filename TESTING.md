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

## Status Code Behavior (Resolved)

From testing, we confirmed:
- **sta=1**: Paused/Running but waiting for power (intermediate state)
- **sta=3**: Diverting (actively heating)
- **sta=6**: Stopped (final stopped state)

### Stop Command Sequence:
Device transitions: `sta=3` → `sta=1` (brief) → `sta=6` (final)
- Takes approximately 30-180 seconds total
- Script waits for `sta=6` before declaring success

### Start Command Sequence:
Device transitions: `sta=6` → `sta=1` (waiting for power) or `sta=3` (if power available)
- Takes approximately 50-100 seconds
- Script accepts `sta=1` or `sta=3` as success

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
| 1 | Paused | Running but not diverting (waiting for power or intermediate state) |
| 3 | Diverting | Actively heating |
| 6 | Stopped | Fully stopped (required for stop command success) |

## Next Steps

1. ✅ **Local testing** - Completed successfully
2. **Merge to main** - Required for GitHub Actions to appear
3. **Test on GitHub** - Use manual trigger after merge
4. **Monitor** first scheduled run
