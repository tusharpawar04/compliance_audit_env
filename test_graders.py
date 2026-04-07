"""Test that graders never return 0.0 or 1.0"""
from server.compliance_environment import ComplianceEnvironment
from models import ComplianceAction

env = ComplianceEnvironment()

# Test all three tasks
for task in ["easy", "medium", "hard"]:
    print(f"\n=== Testing {task} task ===")
    obs = env.reset(task)
    
    # Test 1: Empty action (worst case)
    action_empty = ComplianceAction(
        violation_ids=[],
        explanation="",
        suggested_rewrite=""
    )
    obs = env.step(action_empty)
    print(f"Empty action score: {obs.reward}")
    if obs.reward == 0.0:
        print(f"❌ FAIL: {task} grader returned exactly 0.0")
    elif obs.reward == 1.0:
        print(f"❌ FAIL: {task} grader returned exactly 1.0")
    else:
        print(f"✓ Score is strictly between 0 and 1")
    
    # Test 2: Perfect action (best case)
    env.reset(task)
    actual_violations = env._episode_state.document["violation_ids"]
    rewrite_keywords = env._episode_state.document.get("rewrite_keywords", [])
    
    action_perfect = ComplianceAction(
        violation_ids=actual_violations,
        explanation="Perfect explanation",
        suggested_rewrite=" ".join(rewrite_keywords) if rewrite_keywords else "Perfect rewrite"
    )
    obs = env.step(action_perfect)
    print(f"Perfect action score: {obs.reward}")
    if obs.reward == 0.0:
        print(f"❌ FAIL: {task} grader returned exactly 0.0")
    elif obs.reward == 1.0:
        print(f"❌ FAIL: {task} grader returned exactly 1.0")
    else:
        print(f"✓ Score is strictly between 0 and 1")

print("\n=== All tests complete ===")
