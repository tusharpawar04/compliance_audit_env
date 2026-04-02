"""Debug what the server actually returns"""
import asyncio
import json
import websockets

async def main():
    url = "wss://tusharpawar21-compliance-audit-env.hf.space/ws"
    ws = await websockets.connect(url)
    
    # Reset
    print("=== RESET ===")
    await ws.send(json.dumps({'type': 'reset', 'data': {'task': 'easy'}}))
    response = await ws.recv()
    data = json.loads(response)
    print(json.dumps(data, indent=2))
    
    # Step
    print("\n=== STEP ===")
    await ws.send(json.dumps({
        'type': 'step',
        'data': {
            'violation_ids': ['RULE_01'],
            'explanation': 'Test',
            'suggested_rewrite': ''
        }
    }))
    response = await ws.recv()
    data = json.loads(response)
    print(json.dumps(data, indent=2))
    
    await ws.close()

asyncio.run(main())
