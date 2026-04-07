import requests

# Check health endpoint
try:
    response = requests.get("https://tusharpawar21-compliance-audit-env.hf.space/health", timeout=10)
    print(f"Health endpoint status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error accessing health endpoint: {e}")

# Check main page for version
try:
    response = requests.get("https://tusharpawar21-compliance-audit-env.hf.space/", timeout=10)
    print(f"\nMain page status: {response.status_code}")
    if "1.0.1" in response.text:
        print("✓ Version 1.0.1 detected - Space has rebuilt!")
    else:
        print("✗ Version 1.0.1 not found - Space may still be building")
except Exception as e:
    print(f"Error accessing main page: {e}")
