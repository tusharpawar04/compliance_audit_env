import asyncio
import websockets
import json

async def test():
    url = "wss://tusharpawar21-compliance-audit-env.hf.space/ws"
    print(f"Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as ws:
            print("Connected!")
            
            # Send reset
            reset_msg = {"type": "reset", "data": {"task": "easy"}}
            await ws.send(json.dumps(reset_msg))
            print(f"Sent: {reset_msg}")
            
            # Receive response
            response = await ws.recv()
            print(f"Received: {response[:200]}...")
            
            obs_data = json.loads(response)
            print(f"\nObservation keys: {obs_data.keys()}")
            print(f"Step num: {obs_data.get('step_num')}")
            
            # Send step with empty action
            step_msg = {
                "type": "step",
                "data": {
                    "violation_ids": [],
                    "explanation": "Empty",
                    "suggested_rewrite": ""
                }
            }
            await ws.send(json.dumps(step_msg))
            print(f"\nSent: {step_msg}")
            
            # Receive response
            response = await ws.recv()
            print(f"Received: {response[:300]}...")
            
            obs_data = json.loads(response)
            print(f"\nFull response structure:")
            print(json.dumps(obs_data, indent=2)[:500])
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
