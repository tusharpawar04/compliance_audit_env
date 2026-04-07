"""Monitor HuggingFace Space rebuild status"""
import time
import requests
import asyncio
from client import EnvClient
from models import ComplianceAction

def check_version():
    """Check if Space has version 1.0.1"""
    try:
        response = requests.get("https://tusharpawar21-compliance-audit-env.hf.space/", timeout=10)
        return "1.0.1" in response.text
    except:
        return False

async def test_reward():
    """Test if rewards are non-zero"""
    try:
        client = EnvClient(url="wss://tusharpawar21-compliance-audit-env.hf.space/ws")
        obs = await client.async_reset('easy')
        
        action = ComplianceAction(
            violation_ids=[],
            explanation="Empty",
            suggested_rewrite=""
        )
        
        obs, reward, done, info = await client.async_step(action)
        await client.async_close()
        
        return reward > 0.0
    except:
        return False

async def monitor():
    print("Monitoring HuggingFace Space rebuild...")
    print("Press Ctrl+C to stop\n")
    
    attempt = 1
    while True:
        print(f"[Attempt {attempt}] Checking...", end=" ")
        
        # Check version
        has_version = check_version()
        print(f"Version: {'✓' if has_version else '✗'}", end=" | ")
        
        # Test reward
        reward_ok = await test_reward()
        print(f"Reward: {'✓' if reward_ok else '✗'}")
        
        if has_version and reward_ok:
            print("\n🎉 Space has successfully rebuilt!")
            print("Run 'python test_grader_bounds.py' to verify all graders")
            break
        
        attempt += 1
        print("Waiting 30 seconds...")
        time.sleep(30)

try:
    asyncio.run(monitor())
except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user")
