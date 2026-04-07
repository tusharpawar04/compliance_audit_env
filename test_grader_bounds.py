"""Test grader bounds with actual actions"""
import asyncio
from client import EnvClient
from models import ComplianceAction

async def main():
    print("\n=== Testing Grader Score Bounds ===\n")
    
    client = EnvClient(url="wss://tusharpawar21-compliance-audit-env.hf.space/ws")
    
    for task in ["easy", "medium", "hard"]:
        print(f"[{task.upper()}] Testing...")
        
        # Reset
        obs = await client.async_reset(task)
        
        # Test 1: Empty action (should give minimum score)
        action_empty = ComplianceAction(
            violation_ids=[],
            explanation="Empty",
            suggested_rewrite=""
        )
        obs, reward, done, info = await client.async_step(action_empty)
        print(f"  Empty action reward: {reward}")
        if reward == 0.0:
            print(f"  ❌ FAIL: Returned exactly 0.0")
        elif reward == 1.0:
            print(f"  ❌ FAIL: Returned exactly 1.0")
        elif 0 < reward < 1:
            print(f"  ✓ Valid: {reward} is strictly between 0 and 1")
        
        # Test 2: Action with some violations
        await client.async_reset(task)
        action_some = ComplianceAction(
            violation_ids=["RULE_01", "RULE_02"],
            explanation="Test",
            suggested_rewrite="We will retain data for 30 days and obtain explicit consent."
        )
        obs, reward, done, info = await client.async_step(action_some)
        print(f"  Some violations reward: {reward}")
        if reward == 0.0:
            print(f"  ❌ FAIL: Returned exactly 0.0")
        elif reward == 1.0:
            print(f"  ❌ FAIL: Returned exactly 1.0")
        elif 0 < reward < 1:
            print(f"  ✓ Valid: {reward} is strictly between 0 and 1")
        
        print()
    
    await client.async_close()
    print("=== Test Complete ===\n")

asyncio.run(main())
