import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8765" 

    async with websockets.connect(uri) as websocket:
        message = '{"command": "exchange", "num_of_days": 2, "currencies": ["EUR", "USD"]}'
        await websocket.send(message)

        response = await websocket.recv()
        print(f"Received response from the server: {response}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(send_message())
