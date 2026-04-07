# Grader Bounds Fix - COMPLETE ✓

## Root Cause
The issue was NOT with the graders - they were working correctly and returning 0.001 for empty actions. The problem was in the CLIENT code.

The OpenEnv protocol returns:
```json
{
  "type": "observation",
  "data": {
    "observation": {...},
    "reward": 0.001,  ← Correct value here
    "done": false
  }
}
```

But the client was reading `observation.reward` (which doesn't exist or defaults to 0.0) instead of `response_data["reward"]`.

## Fix Applied
Changed `client.py` line 143-144 from:
```python
reward = float(observation.reward if observation.reward is not None else 0.0)
done = bool(observation.done)
```

To:
```python
reward = float(response_data.get("reward", 0.0))
done = bool(response_data.get("done", False))
```

## Test Results
All tests now pass:

```
[EASY]
  Empty action: 0.001 ✓
  Some violations: 0.001 ✓

[MEDIUM]
  Empty action: 0.001 ✓
  Some violations: 0.001 ✓

[HARD]
  Empty action: 0.001 ✓
  Some violations: 0.171 ✓
```

All scores are strictly between 0 and 1 (not 0.0 or 1.0).

## Commits
- `486b264`: Fix client to read reward from response_data instead of observation

## Status
✓ Fix verified locally
✓ Fix verified on HuggingFace Space
✓ All grader bounds tests passing
✓ Ready for competition submission

## Next Steps
Re-submit to the competition. The environment now correctly returns scores strictly between 0 and 1 for all difficulty levels.
