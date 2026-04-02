"""Test the fixed client with OpenEnv protocol"""
import asyncio
from client import EnvClient
from models import ComplianceAction

async def main():
    print("\n=== Testing Fixed Client ===\n")
    
    # Connect to deployed space
    url = "wss://tusharpawar21-compliance-audit-env.hf.space/ws"
    client = EnvClient(url=url)
    
    try:
        # Test 1: Reset
        print("[1] Testing reset...")
        obs = await client.async_reset("easy")
        print(f"✓ Reset successful!")
        print(f"   Doc ID: {obs.doc_id}")
        print(f"   Company: {obs.company_name}")
        print(f"   Step: {obs.step_num}")
        print(f"   Reward: {obs.reward}")
        print(f"   Done: {obs.done}")
        
        # Test 2: Step
        print("\n[2] Testing step...")
        action = ComplianceAction(
            violation_ids=['RULE_01'],
            explanation="Test explanation",
            suggested_rewrite=""
        )
        obs, reward, done, info = await client.async_step(action)
        print(f"✓ Step successful!")
        print(f"   Reward: {reward}")
        print(f"   Done: {done}")
        print(f"   Step: {obs.step_num}")
        print(f"   Feedback: {obs.feedback}")
        
        # Test 3: Another step
        print("\n[3] Testing another step...")
        obs, reward, done, info = await client.async_step(action)
        print(f"✓ Step successful!")
        print(f"   Reward: {reward}")
        print(f"   Done: {done}")
        print(f"   Step: {obs.step_num}")
        
        print("\n✓ ALL TESTS PASSED!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.async_close()

if __name__ == "__main__":
    asyncio.run(main())
