import asyncio
from client import EnvClient
from models import ComplianceAction

async def test():
    print("Testing single step...")
    client = EnvClient(url='wss://tusharpawar21-compliance-audit-env.hf.space/ws')
    
    # Reset
    obs = await client.async_reset('easy')
    print(f"Reset successful, step_num: {obs.step_num}")
    
    # Empty action
    action = ComplianceAction(
        violation_ids=[],
        explanation="Empty test",
        suggested_rewrite=""
    )
    
    print("Sending step...")
    obs, reward, done, info = await client.async_step(action)
    print(f"Step complete!")
    print(f"  Reward: {reward}")
    print(f"  Done: {done}")
    print(f"  Step num: {obs.step_num}")
    
    if reward == 0.0:
        print("  ❌ FAIL: Returned exactly 0.0")
    elif reward == 1.0:
        print("  ❌ FAIL: Returned exactly 1.0")
    elif 0 < reward < 1:
        print(f"  ✓ PASS: {reward} is strictly between 0 and 1")
    
    await client.async_close()
    print("Test complete")

asyncio.run(test())
