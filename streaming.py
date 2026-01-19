import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def message_stream():
    """Generate messages dynamically."""
    yield {"type": "user", "message": {"role": "user", "content": "Analyze the following data:"}}
    await asyncio.sleep(0.5)
    yield {"type": "user", "message": {"role": "user", "content": "Temperature: 25°C"}}
    await asyncio.sleep(0.5)
    yield {"type": "user", "message": {"role": "user", "content": "Humidity: 60%"}}
    await asyncio.sleep(0.5)
    yield {"type": "user", "message": {"role": "user", "content": "What patterns do you see?"}}

async def main():
    async with ClaudeSDKClient() as client:
        # Stream input to Claude
        await client.query(message_stream())

        # Process response
        async for message in client.receive_response():
            print(message)

        # Follow-up in same session
        await client.query("Should we be concerned about these readings?")

        async for message in client.receive_response():
            print(message)

asyncio.run(main())