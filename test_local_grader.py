"""Test graders locally without server"""
from server.compliance_environment import ComplianceEnvironment
from models import ComplianceAction

env = ComplianceEnvironment()

print("Testing graders locally...\n")

for task in ["easy", "medium", "hard"]:
    print(f"[{task.upper()}]")
    
    # Reset
    obs = env.reset(task)
    
    # Test empty action
    action_empty = ComplianceAction(
        violation_ids=[],
        explanation="Empty",
        suggested_rewrite=""
    )
    
    obs = env.step(action_empty)
    reward = obs.reward
    
    print(f"  Empty action reward: {reward}")
    if reward == 0.0:
        print(f"  ❌ FAIL: Returned exactly 0.0")
    elif reward == 1.0:
        print(f"  ❌ FAIL: Returned exactly 1.0")
    elif 0 < reward < 1:
        print(f"  ✓ PASS: {reward} is strictly between 0 and 1")
    else:
        print(f"  ❌ FAIL: Invalid reward {reward}")
    
    # Reset and test with some violations
    obs = env.reset(task)
    action_some = ComplianceAction(
        violation_ids=["RULE_01", "RULE_02"],
        explanation="Test",
        suggested_rewrite="We will retain data for 30 days and obtain explicit consent."
    )
    
    obs = env.step(action_some)
    reward = obs.reward
    
    print(f"  Some violations reward: {reward}")
    if reward == 0.0:
        print(f"  ❌ FAIL: Returned exactly 0.0")
    elif reward == 1.0:
        print(f"  ❌ FAIL: Returned exactly 1.0")
    elif 0 < reward < 1:
        print(f"  ✓ PASS: {reward} is strictly between 0 and 1")
    else:
        print(f"  ❌ FAIL: Invalid reward {reward}")
    
    print()

print("Local test complete")
