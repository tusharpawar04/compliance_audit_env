"""
DEEP SWEEP ANALYSIS - Finding ALL Major Errors
================================================

This script performs a comprehensive analysis of the compliance audit environment
to identify ALL major errors before submission.
"""

import asyncio
import json
import sys
import traceback
import websockets
from typing import Dict, List, Any

# Test results storage
errors_found: List[Dict[str, Any]] = []
warnings_found: List[Dict[str, Any]] = []
passed_checks: List[str] = []


def log_error(category: str, description: str, details: str = ""):
    """Log a critical error"""
    errors_found.append({
        "category": category,
        "description": description,
        "details": details,
        "severity": "CRITICAL"
    })
    print(f"\n❌ CRITICAL ERROR [{category}]")
    print(f"   {description}")
    if details:
        print(f"   Details: {details}")


def log_warning(category: str, description: str, details: str = ""):
    """Log a warning"""
    warnings_found.append({
        "category": category,
        "description": description,
        "details": details,
        "severity": "WARNING"
    })
    print(f"\n⚠️  WARNING [{category}]")
    print(f"   {description}")
    if details:
        print(f"   Details: {details}")


def log_pass(check_name: str):
    """Log a passed check"""
    passed_checks.append(check_name)
    print(f"✓ {check_name}")


async def test_websocket_protocol():
    """Test WebSocket protocol compliance"""
    print("\n" + "="*60)
    print("TESTING: WebSocket Protocol Compliance")
    print("="*60)
    
    try:
        # Connect to deployed space
        url = 'wss://tusharpawar21-compliance-audit-env.hf.space/ws'
        print(f"\nConnecting to: {url}")
        
        ws = await asyncio.wait_for(websockets.connect(url), timeout=10)
        log_pass("WebSocket connection established")
        
        # Test 1: Reset with default task
        print("\n[Test 1] Reset with default task...")
        await ws.send(json.dumps({'type': 'reset'}))
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(response)
        
        if data.get('type') == 'error':
            log_error("RESET_DEFAULT", 
                     "Reset with default task failed",
                     data.get('data', {}).get('message', str(data)))
        else:
            log_pass("Reset with default task")
            
        # Test 2: Reset with explicit task
        print("\n[Test 2] Reset with explicit task='easy'...")
        await ws.send(json.dumps({'type': 'reset', 'data': {'task': 'easy'}}))
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(response)
        
        if data.get('type') == 'error':
            log_error("RESET_EXPLICIT",
                     "Reset with explicit task='easy' failed",
                     data.get('data', {}).get('message', str(data)))
        else:
            obs = data.get('data', {}).get('observation', {})
            if not obs.get('doc_id'):
                log_error("RESET_OBSERVATION", "Reset observation missing doc_id")
            if not obs.get('document_text'):
                log_error("RESET_OBSERVATION", "Reset observation missing document_text")
            if obs.get('step_num') != 1:
                log_error("RESET_OBSERVATION", f"Reset step_num should be 1, got {obs.get('step_num')}")
            if 'reward' not in obs:
                log_error("RESET_OBSERVATION", "Reset observation missing 'reward' field")
            if 'done' not in obs:
                log_error("RESET_OBSERVATION", "Reset observation missing 'done' field")
            
            if not errors_found or errors_found[-1]['category'] != 'RESET_OBSERVATION':
                log_pass("Reset observation structure valid")
        
        # Test 3: Step with flat action format
        print("\n[Test 3] Step with flat action format...")
        msg_flat = {
            'type': 'step',
            'data': {
                'violation_ids': ['RULE_01'],
                'explanation': 'Test explanation',
                'suggested_rewrite': ''
            }
        }
        await ws.send(json.dumps(msg_flat))
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        data_flat = json.loads(response)
        
        flat_works = data_flat.get('type') != 'error'
        
        # Test 4: Step with nested action format (already correct format)
        print("\n[Test 4] Testing step response...")
        # Reset first
        await ws.send(json.dumps({'type': 'reset', 'data': {'task': 'easy'}}))
        await asyncio.wait_for(ws.recv(), timeout=5)
        
        # Step is already in correct format
        await ws.send(json.dumps(msg_flat))
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(response)
        
        step_works = data.get('type') != 'error'
        
        # Determine result
        if not step_works:
            log_error("STEP_FORMAT",
                     "Step action format failed",
                     f"Response: {json.dumps(data)[:200]}")
        else:
            log_pass("Step with correct action format works")
        
        # Test 5: Step response structure
        if step_works:
            print("\n[Test 5] Validating step response structure...")
            step_data = data.get('data', {})
            
            if 'observation' not in step_data:
                log_error("STEP_RESPONSE", "Step response missing 'observation' field")
            
            obs = step_data.get('observation', {})
            if 'reward' not in obs:
                log_error("STEP_OBSERVATION", "Step observation missing 'reward' field")
            if 'done' not in obs:
                log_error("STEP_OBSERVATION", "Step observation missing 'done' field")
            if obs.get('step_num', 0) < 1:
                log_error("STEP_OBSERVATION", f"Step observation has invalid step_num: {obs.get('step_num')}")
            
            if not errors_found or 'STEP_' not in errors_found[-1]['category']:
                log_pass("Step response structure valid")
        
        # Test 6: State endpoint
        print("\n[Test 6] Testing state endpoint...")
        await ws.send(json.dumps({'type': 'state'}))
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(response)
        
        if data.get('type') == 'error':
            log_error("STATE_ENDPOINT",
                     "State endpoint failed",
                     data.get('data', {}).get('message', str(data)))
        else:
            log_pass("State endpoint works")
        
        await ws.close()
        
    except asyncio.TimeoutError:
        log_error("WEBSOCKET_TIMEOUT", "WebSocket operation timed out")
    except websockets.exceptions.WebSocketException as e:
        log_error("WEBSOCKET_CONNECTION", f"WebSocket error: {str(e)}")
    except Exception as e:
        log_error("WEBSOCKET_GENERAL", f"Unexpected error: {str(e)}", traceback.format_exc())


async def test_environment_logic():
    """Test environment logic and grading"""
    print("\n" + "="*60)
    print("TESTING: Environment Logic & Grading")
    print("="*60)
    
    # Import local modules
    try:
        from server.compliance_environment import ComplianceEnvironment
        from models import ComplianceAction
        
        env = ComplianceEnvironment()
        
        # Test 1: Reset returns correct structure
        print("\n[Test 1] Testing reset() return structure...")
        obs = env.reset("easy")
        
        if not hasattr(obs, 'reward'):
            log_error("ENV_RESET", "Reset observation missing 'reward' attribute")
        elif obs.reward != 0.0:
            log_error("ENV_RESET", f"Reset observation reward should be 0.0, got {obs.reward}")
        
        if not hasattr(obs, 'done'):
            log_error("ENV_RESET", "Reset observation missing 'done' attribute")
        elif obs.done != False:
            log_error("ENV_RESET", f"Reset observation done should be False, got {obs.done}")
        
        if obs.step_num != 1:
            log_error("ENV_RESET", f"Reset observation step_num should be 1, got {obs.step_num}")
        
        if not errors_found or 'ENV_RESET' not in errors_found[-1]['category']:
            log_pass("Environment reset() structure valid")
        
        # Test 2: Step returns correct structure
        print("\n[Test 2] Testing step() return structure...")
        action = ComplianceAction(
            violation_ids=['RULE_01'],
            explanation="Test",
            suggested_rewrite=""
        )
        
        obs = env.step(action)
        
        if not hasattr(obs, 'reward'):
            log_error("ENV_STEP", "Step observation missing 'reward' attribute")
        if not hasattr(obs, 'done'):
            log_error("ENV_STEP", "Step observation missing 'done' attribute")
        if obs.step_num < 2:
            log_error("ENV_STEP", f"Step observation step_num should be >= 2, got {obs.step_num}")
        
        if not errors_found or 'ENV_STEP' not in errors_found[-1]['category']:
            log_pass("Environment step() structure valid")
        
        # Test 3: Grading functions
        print("\n[Test 3] Testing grading functions...")
        
        # Test easy grader
        env.reset("easy")
        action_correct = ComplianceAction(
            violation_ids=env._episode_state.document['violation_ids'],
            explanation="Correct",
            suggested_rewrite=""
        )
        score = env._grade_easy(action_correct)
        if score != 1.0:
            log_warning("GRADING_EASY", f"Easy grader with perfect action should return 1.0, got {score}")
        else:
            log_pass("Easy grader works correctly")
        
        # Test medium grader
        env.reset("medium")
        score = env._grade_medium(action_correct)
        if score < 0 or score > 1:
            log_error("GRADING_MEDIUM", f"Medium grader returned invalid score: {score}")
        else:
            log_pass("Medium grader works correctly")
        
        # Test hard grader
        env.reset("hard")
        action_with_rewrite = ComplianceAction(
            violation_ids=env._episode_state.document['violation_ids'],
            explanation="Correct",
            suggested_rewrite="We will retain data for 30 days and obtain explicit consent."
        )
        score = env._grade_hard(action_with_rewrite)
        if score < 0 or score > 1:
            log_error("GRADING_HARD", f"Hard grader returned invalid score: {score}")
        else:
            log_pass("Hard grader works correctly")
        
    except ImportError as e:
        log_error("IMPORT", f"Failed to import modules: {str(e)}")
    except Exception as e:
        log_error("ENV_LOGIC", f"Environment logic error: {str(e)}", traceback.format_exc())


def test_file_structure():
    """Test file structure and required files"""
    print("\n" + "="*60)
    print("TESTING: File Structure & Required Files")
    print("="*60)
    
    import os
    
    required_files = [
        'server/app.py',
        'server/compliance_environment.py',
        'server/compliance_data.py',
        'models.py',
        'client.py',
        'inference.py',
        'openenv.yaml',
        'Dockerfile',
        'README.md',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            log_pass(f"Required file exists: {file_path}")
        else:
            log_error("FILE_MISSING", f"Required file missing: {file_path}")
    
    # Check openenv.yaml structure
    print("\n[Checking openenv.yaml structure...]")
    try:
        import yaml
        with open('openenv.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['name', 'version', 'description', 'tasks']
        for key in required_keys:
            if key not in config:
                log_error("OPENENV_YAML", f"Missing required key: {key}")
        
        if 'tasks' in config:
            expected_tasks = ['easy', 'medium', 'hard']
            if config['tasks'] != expected_tasks:
                log_warning("OPENENV_YAML", f"Tasks should be {expected_tasks}, got {config['tasks']}")
        
        if not errors_found or 'OPENENV_YAML' not in errors_found[-1]['category']:
            log_pass("openenv.yaml structure valid")
    
    except Exception as e:
        log_error("OPENENV_YAML", f"Failed to parse openenv.yaml: {str(e)}")


def test_models():
    """Test Pydantic models"""
    print("\n" + "="*60)
    print("TESTING: Pydantic Models")
    print("="*60)
    
    try:
        from models import ComplianceAction, ComplianceObservation, ComplianceReward
        
        # Test ComplianceAction
        print("\n[Test 1] Testing ComplianceAction model...")
        action = ComplianceAction(
            violation_ids=['RULE_01'],
            explanation="Test",
            suggested_rewrite=""
        )
        log_pass("ComplianceAction model works")
        
        # Test ComplianceObservation
        print("\n[Test 2] Testing ComplianceObservation model...")
        obs = ComplianceObservation(
            doc_id="test",
            company_name="Test Co",
            document_text="Test document",
            rules_reference="Rules",
            task_name="easy",
            step_num=1,
            feedback="",
            previous_score=0.0,
            reward=0.0,
            done=False
        )
        
        # Check required fields
        if not hasattr(obs, 'reward'):
            log_error("MODEL_OBSERVATION", "ComplianceObservation missing 'reward' field")
        if not hasattr(obs, 'done'):
            log_error("MODEL_OBSERVATION", "ComplianceObservation missing 'done' field")
        
        if not errors_found or 'MODEL_OBSERVATION' not in errors_found[-1]['category']:
            log_pass("ComplianceObservation model works")
        
        # Test ComplianceReward
        print("\n[Test 3] Testing ComplianceReward model...")
        reward = ComplianceReward(score=0.5)
        log_pass("ComplianceReward model works")
        
    except ImportError as e:
        log_error("MODEL_IMPORT", f"Failed to import models: {str(e)}")
    except Exception as e:
        log_error("MODEL_VALIDATION", f"Model validation error: {str(e)}", traceback.format_exc())


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "DEEP SWEEP ANALYSIS")
    print(" "*10 + "Compliance Audit Environment")
    print("="*70)
    
    # Run all test suites
    test_file_structure()
    test_models()
    await test_environment_logic()
    await test_websocket_protocol()
    
    # Print summary
    print("\n" + "="*70)
    print(" "*25 + "SUMMARY")
    print("="*70)
    
    print(f"\n✓ Passed Checks: {len(passed_checks)}")
    print(f"⚠️  Warnings: {len(warnings_found)}")
    print(f"❌ Critical Errors: {len(errors_found)}")
    
    if errors_found:
        print("\n" + "="*70)
        print("CRITICAL ERRORS THAT MUST BE FIXED:")
        print("="*70)
        for i, error in enumerate(errors_found, 1):
            print(f"\n{i}. [{error['category']}] {error['description']}")
            if error['details']:
                print(f"   Details: {error['details'][:200]}")
    
    if warnings_found:
        print("\n" + "="*70)
        print("WARNINGS (Should be reviewed):")
        print("="*70)
        for i, warning in enumerate(warnings_found, 1):
            print(f"\n{i}. [{warning['category']}] {warning['description']}")
            if warning['details']:
                print(f"   Details: {warning['details'][:200]}")
    
    print("\n" + "="*70)
    if errors_found:
        print("❌ SUBMISSION NOT READY - Fix critical errors first")
        sys.exit(1)
    elif warnings_found:
        print("⚠️  SUBMISSION READY WITH WARNINGS - Review warnings before submitting")
        sys.exit(0)
    else:
        print("✓ ALL CHECKS PASSED - Ready for submission!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
