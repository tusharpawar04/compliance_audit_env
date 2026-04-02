# CRITICAL FIXES NEEDED FOR OPENENV PROTOCOL COMPLIANCE

## Issue Summary
The compliance audit environment is NOT compliant with the OpenEnv WebSocket protocol specification. The OpenEnv protocol expects all parameters to be nested under a `data` field, but our implementation expects them at the top level.

## Root Cause
Looking at the OpenEnv types (`openenv.core.env_server.types`):

```python
class WSResetMessage(BaseModel):
    type: Literal["reset"] = Field(default="reset")
    data: Dict[str, Any] = Field(default_factory=dict)  # ← Parameters go HERE

class WSStepMessage(BaseModel):
    type: Literal["step"] = Field(default="step")
    data: Dict[str, Any] = Field(...)  # ← Action goes HERE
```

## Current (WRONG) Message Format
```json
// Reset
{"type": "reset", "task": "easy"}

// Step
{"type": "step", "violation_ids": [...], "explanation": "...", "suggested_rewrite": ""}
```

## Correct OpenEnv Message Format
```json
// Reset
{"type": "reset", "data": {"task": "easy"}}

// Step  
{"type": "step", "data": {"violation_ids": [...], "explanation": "...", "suggested_rewrite": ""}}
```

## Files That Need Fixing

### 1. NO CHANGES NEEDED TO SERVER CODE
The `create_app()` function from `openenv.core.env_server` already handles the protocol correctly. Our environment implementation is fine - it's just the message format that clients need to use.

### 2. client.py - Update WebSocket Message Format
**Current code sends wrong format:**
```python
message = {
    "type": "reset",
    "task": task  # ← WRONG: should be nested under 'data'
}
```

**Should be:**
```python
message = {
    "type": "reset",
    "data": {"task": task}  # ← CORRECT: nested under 'data'
}
```

**And for step:**
```python
message = {
    "type": "step",
    "data": action.model_dump()  # ← CORRECT: action nested under 'data'
}
```

### 3. inference.py - Already Correct!
The inference.py file is already using the client.py, so once we fix client.py, inference.py will work correctly.

### 4. Response Format - Already Correct!
The OpenEnv protocol returns responses in this format:
```json
{
  "type": "observation",
  "data": {
    "observation": {...},
    "reward": 0.5,
    "done": false
  }
}
```

Our environment already returns the correct format because `create_app()` handles it.

## Testing After Fix

### Test 1: Reset with default task
```python
await ws.send(json.dumps({'type': 'reset', 'data': {}}))
```

### Test 2: Reset with explicit task
```python
await ws.send(json.dumps({'type': 'reset', 'data': {'task': 'easy'}}))
```

### Test 3: Step
```python
await ws.send(json.dumps({
    'type': 'step',
    'data': {
        'violation_ids': ['RULE_01'],
        'explanation': 'Test',
        'suggested_rewrite': ''
    }
}))
```

## Impact Assessment

### Critical (Must Fix):
1. ✅ client.py - async_reset() method
2. ✅ client.py - async_step() method

### No Changes Needed:
1. ✅ server/app.py - Already correct (uses create_app)
2. ✅ server/compliance_environment.py - Already correct
3. ✅ models.py - Already correct
4. ✅ inference.py - Will work once client.py is fixed

## Estimated Fix Time
- 5 minutes to update client.py
- 5 minutes to test locally
- 5 minutes to push to HuggingFace
- Total: 15 minutes

## Confidence Level
100% - This is the exact issue causing "Invalid message" errors. The OpenEnv protocol specification is clear and our current implementation doesn't match it.
