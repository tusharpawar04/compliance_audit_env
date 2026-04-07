"""Comprehensive pre-submission validation"""
import sys
import traceback

print("="*70)
print("PRE-SUBMISSION VALIDATION")
print("="*70)

errors = []
warnings = []

# Test 1: Import all modules
print("\n[1/8] Testing imports...")
try:
    from server.compliance_environment import ComplianceEnvironment
    from models import ComplianceAction, ComplianceObservation
    from server.compliance_data import DOCUMENTS, RULES
    print("  ✓ All imports successful")
except Exception as e:
    errors.append(f"Import failed: {e}")
    print(f"  ✗ Import failed: {e}")
    traceback.print_exc()

# Test 2: Instantiate environment
print("\n[2/8] Testing environment instantiation...")
try:
    env = ComplianceEnvironment()
    print("  ✓ Environment instantiated")
except Exception as e:
    errors.append(f"Environment instantiation failed: {e}")
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check graders property
print("\n[3/8] Testing graders property...")
try:
    graders = env.graders
    print(f"  ✓ Graders property exists: {list(graders.keys())}")
    
    if len(graders) < 3:
        errors.append(f"Not enough graders: {len(graders)} (need 3)")
        print(f"  ✗ Only {len(graders)} graders found (need 3)")
    
    expected_tasks = ["easy", "medium", "hard"]
    for task in expected_tasks:
        if task not in graders:
            errors.append(f"Missing grader for task: {task}")
            print(f"  ✗ Missing grader for: {task}")
        else:
            print(f"  ✓ Grader exists for: {task}")
            
except AttributeError:
    errors.append("Environment missing 'graders' property")
    print("  ✗ Environment missing 'graders' property")
except Exception as e:
    errors.append(f"Graders check failed: {e}")
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()

# Test 4: Test reset for all tasks
print("\n[4/8] Testing reset for all tasks...")
for task in ["easy", "medium", "hard"]:
    try:
        obs = env.reset(task)
        print(f"  ✓ Reset successful for: {task}")
        
        # Verify observation structure
        if not hasattr(obs, 'reward'):
            warnings.append(f"{task}: Observation missing 'reward' field")
        if not hasattr(obs, 'done'):
            warnings.append(f"{task}: Observation missing 'done' field")
            
    except Exception as e:
        errors.append(f"Reset failed for {task}: {e}")
        print(f"  ✗ Reset failed for {task}: {e}")
        traceback.print_exc()

# Test 5: Test graders with empty action
print("\n[5/8] Testing graders with empty action...")
for task in ["easy", "medium", "hard"]:
    try:
        env.reset(task)
        action = ComplianceAction(
            violation_ids=[],
            explanation="Test",
            suggested_rewrite=""
        )
        obs = env.step(action)
        reward = obs.reward
        
        print(f"  {task}: reward = {reward}")
        
        # Check reward bounds
        if reward <= 0.0:
            errors.append(f"{task}: Reward {reward} is <= 0.0 (must be > 0)")
            print(f"    ✗ Reward {reward} is <= 0.0")
        elif reward >= 1.0:
            errors.append(f"{task}: Reward {reward} is >= 1.0 (must be < 1)")
            print(f"    ✗ Reward {reward} is >= 1.0")
        else:
            print(f"    ✓ Reward {reward} is in valid range (0, 1)")
            
    except Exception as e:
        errors.append(f"Grader test failed for {task}: {e}")
        print(f"  ✗ Failed for {task}: {e}")
        traceback.print_exc()

# Test 6: Test graders with some violations
print("\n[6/8] Testing graders with violations...")
for task in ["easy", "medium", "hard"]:
    try:
        env.reset(task)
        action = ComplianceAction(
            violation_ids=["RULE_01", "RULE_02"],
            explanation="Test violations",
            suggested_rewrite="We will retain data for 30 days and obtain explicit consent."
        )
        obs = env.step(action)
        reward = obs.reward
        
        print(f"  {task}: reward = {reward}")
        
        if reward <= 0.0 or reward >= 1.0:
            errors.append(f"{task}: Reward {reward} out of range (0, 1)")
            print(f"    ✗ Reward out of range")
        else:
            print(f"    ✓ Reward in valid range")
            
    except Exception as e:
        errors.append(f"Violation test failed for {task}: {e}")
        print(f"  ✗ Failed for {task}: {e}")
        traceback.print_exc()

# Test 7: Check openenv.yaml
print("\n[7/8] Checking openenv.yaml...")
try:
    import yaml
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Check required fields
    required_fields = ["name", "version", "description", "tasks", "graders"]
    for field in required_fields:
        if field not in config:
            errors.append(f"openenv.yaml missing field: {field}")
            print(f"  ✗ Missing field: {field}")
        else:
            print(f"  ✓ Field exists: {field}")
    
    # Check tasks
    if "tasks" in config:
        tasks = config["tasks"]
        if len(tasks) < 3:
            errors.append(f"openenv.yaml has only {len(tasks)} tasks (need 3)")
            print(f"  ✗ Only {len(tasks)} tasks")
        else:
            print(f"  ✓ {len(tasks)} tasks defined: {tasks}")
    
    # Check graders
    if "graders" in config:
        graders_config = config["graders"]
        if len(graders_config) < 3:
            errors.append(f"openenv.yaml has only {len(graders_config)} graders (need 3)")
            print(f"  ✗ Only {len(graders_config)} graders")
        else:
            print(f"  ✓ {len(graders_config)} graders defined: {list(graders_config.keys())}")
            
except FileNotFoundError:
    errors.append("openenv.yaml not found")
    print("  ✗ openenv.yaml not found")
except Exception as e:
    errors.append(f"openenv.yaml check failed: {e}")
    print(f"  ✗ Failed: {e}")
    traceback.print_exc()

# Test 8: Check critical files exist
print("\n[8/8] Checking critical files...")
critical_files = [
    "server/compliance_environment.py",
    "server/compliance_data.py",
    "server/app.py",
    "models.py",
    "client.py",
    "Dockerfile",
    "pyproject.toml",
    "openenv.yaml"
]

import os
for filepath in critical_files:
    if os.path.exists(filepath):
        print(f"  ✓ {filepath}")
    else:
        errors.append(f"Missing file: {filepath}")
        print(f"  ✗ Missing: {filepath}")

# Summary
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)

if warnings:
    print(f"\n⚠️  {len(warnings)} WARNING(S):")
    for w in warnings:
        print(f"  - {w}")

if errors:
    print(f"\n✗ {len(errors)} ERROR(S) FOUND:")
    for e in errors:
        print(f"  - {e}")
    print("\n❌ VALIDATION FAILED - FIX ERRORS BEFORE SUBMITTING")
    sys.exit(1)
else:
    print("\n✓ ALL CHECKS PASSED")
    print("✓ Environment is ready for submission")
    sys.exit(0)
