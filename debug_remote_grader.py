"""Debug what's happening on the remote server"""
import asyncio
import json
import websockets

async def test():
    url = "wss://tusharpawar21-compliance-audit-env.hf.space/ws"
    
    async with websockets.connect(url) as ws:
        # Reset
        await ws.send(json.dumps({"type": "reset", "data": {"task": "easy"}}))
        response = json.loads(await ws.recv())
        print("Reset response keys:", response.get("data", {}).keys())
        
        # Step with empty action
        await ws.send(json.dumps({
            "type": "step",
            "data": {
                "violation_ids": [],
                "explanation": "Empty",
                "suggested_rewrite": ""
            }
        }))
        
        response = json.loads(await ws.recv())
        print("\nStep response structure:")
        print(json.dumps(response, indent=2))

asyncio.run(test())
