"""Comprehensive environment test"""
import asyncio
import json
import websockets

async def main():
    print("\n=== COMPREHENSIVE ENVIRONMENT TEST ===\n")
    
    ws = await websockets.connect('wss://tusharpawar21-compliance-audit-env.hf.space/ws')
    
    # Test 1: Reset
    print("[1] Testing reset...")
    await ws.send(json.dumps({'type': 'reset'}))
    r = await ws.recv()
    d = json.loads(r)
    if d['type'] == 'error':
        print(f"✗ Reset failed: {d['data']['message']}")
        return
    print(f"✓ Reset OK - Doc: {d['data']['observation']['doc_id']}")
    
    # Test 2: Step with just action fields (not nested)
    print("\n[2] Testing step (flat action)...")
    msg = {
        'type': 'step',
        'violation_ids': ['RULE_01'],
        'explanation': 'Test',
        'suggested_rewrite': ''
    }
    print(f"Sending: {json.dumps(msg)}")
    await ws.send(json.dumps(msg))
    r = await ws.recv()
    d = json.loads(r)
    print(f"Full response: {json.dumps(d, indent=2)[:500]}")
    print(f"Response type: {d['type']}")
    if d['type'] == 'error':
        print(f"✗ Failed: {d['data']}")
        
        # Test 3: Try nested action
        print("\n[3] Testing step (nested action)...")
        msg2 = {
            'type': 'step',
            'action': {
                'violation_ids': ['RULE_01'],
                'explanation': 'Test',
                'suggested_rewrite': ''
            }
        }
        await ws.send(json.dumps(msg2))
        r = await ws.recv()
        d = json.loads(r)
        print(f"Response type: {d['type']}")
        if d['type'] == 'error':
            print(f"✗ Failed: {d['data']['message']}")
        else:
            print(f"✓ Step OK - Reward: {d['data']['reward']}")
    else:
        print(f"✓ Step OK - Reward: {d['data']['reward']}")
    
    await ws.close()
    print("\n=== TEST COMPLETE ===\n")

asyncio.run(main())
