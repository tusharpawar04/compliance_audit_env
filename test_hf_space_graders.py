"""Test if HuggingFace Space has the graders working"""
import requests
import json

print("Testing HuggingFace Space...")
print("="*70)

# Test 1: Check if Space is responding
print("\n[1] Testing /health endpoint...")
try:
    response = requests.get("https://tusharpawar21-compliance-audit-env.hf.space/health", timeout=10)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text}")
except Exception as e:
    print(f"  Error: {e}")

# Test 2: Test reset
print("\n[2] Testing /reset endpoint...")
try:
    response = requests.post(
        "https://tusharpawar21-compliance-audit-env.hf.space/reset",
        json={"task": "easy"},
        timeout=10
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response keys: {list(data.keys())}")
    else:
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Test step with empty action
print("\n[3] Testing /step endpoint with empty action...")
try:
    # First reset
    requests.post(
        "https://tusharpawar21-compliance-audit-env.hf.space/reset",
        json={"task": "easy"},
        timeout=10
    )
    
    # Then step
    response = requests.post(
        "https://tusharpawar21-compliance-audit-env.hf.space/step",
        json={
            "violation_ids": [],
            "explanation": "Test",
            "suggested_rewrite": ""
        },
        timeout=10
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response keys: {list(data.keys())}")
        if 'reward' in data:
            print(f"  Reward: {data['reward']}")
        if 'observation' in data and 'reward' in data['observation']:
            print(f"  Observation reward: {data['observation']['reward']}")
    else:
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("Test complete")
