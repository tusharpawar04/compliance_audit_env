# Grader Score Bounds Fix

## Issue
Submission validation failed with:
```
Phase 2 Failed
Not enough tasks with graders · One or more task scores are out of range
Your submission must include at least 3 tasks with graders. 
Each task's score must be strictly between 0 and 1 (not 0.0 and not 1.0).
```

## Root Cause
The grading functions could return exactly 0.0 or 1.0:
- Returning 0.0 when no violations were predicted
- Returning 1.0 when all violations were perfectly identified

## Fix Applied

### Modified Functions
All three grading functions in `server/compliance_environment.py`:

1. **_grade_easy()** - F1 score grader
2. **_grade_medium()** - Partial credit grader  
3. **_grade_hard()** - Composite grader

### Changes Made

#### Before (could return 0.0 or 1.0):
```python
if len(predicted) == 0:
    return 0.0  # ❌ Exactly 0.0

f1 = 2 * precision * recall / (precision + recall)
return f1  # ❌ Could be exactly 1.0
```

#### After (strictly between 0 and 1):
```python
if len(predicted) == 0:
    return 0.001  # ✓ Minimum 0.001

f1 = 2 * precision * recall / (precision + recall)
return max(0.001, min(0.999, f1))  # ✓ Clamped to (0.001, 0.999)
```

### Implementation Details

**Minimum Score**: 0.001
- Returned for empty predictions
- Returned for zero actual violations
- Returned when precision + recall = 0

**Maximum Score**: 0.999
- Applied via clamping: `min(0.999, score)`
- Prevents perfect scores from being exactly 1.0

**Clamping Function**:
```python
return max(0.001, min(0.999, score))
```

This ensures:
- `score < 0.001` → returns 0.001
- `0.001 ≤ score ≤ 0.999` → returns score
- `score > 0.999` → returns 0.999

## Verification

All three tasks (easy, medium, hard) now have graders that:
- ✅ Return scores strictly between 0 and 1
- ✅ Never return exactly 0.0
- ✅ Never return exactly 1.0
- ✅ Maintain relative scoring (better actions get higher scores)

## Files Modified

- `server/compliance_environment.py`
  - `_grade_easy()` - Added clamping
  - `_grade_medium()` - Added clamping
  - `_grade_hard()` - Added clamping

## Deployment Status

- ✅ Committed to GitHub (commit: 3f9c025)
- ✅ Pushed to HuggingFace Space
- ⏳ Space rebuilding with new code

## Expected Behavior

After deployment:
- Empty actions: score ≈ 0.001
- Partial matches: score between 0.001 and 0.999
- Perfect matches: score ≈ 0.999 (not 1.0)

This satisfies the submission requirement that all task scores must be strictly between 0 and 1.
