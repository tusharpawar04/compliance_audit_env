import asyncio
from client import EnvClient

async def test():
    client = EnvClient(url='wss://tusharpawar21-compliance-audit-env.hf.space/ws')
    obs = await client.async_reset('easy')
    print(f'Connected! Document text preview: {obs.document_text[:50]}...')
    print(f'Step num: {obs.step_num}')
    await client.async_close()

asyncio.run(test())
