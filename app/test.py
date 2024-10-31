import asyncio
import json

import websockets
from fastapi_websocket_pubsub import PubSubClient


async def subscribe_parking_and_send(parking_place_id: int, level: int):
    async def on_events(data, topic):
        print(f"running callback for {topic}!")

    async def on_steel(data, topic):
        print(f"running callback {topic}!")
        print("Got data", data)

    client = PubSubClient([f"{parking_place_id}/{level}"], callback=on_events)
    client.subscribe(f"{parking_place_id}/{level}", on_steel)
    client.start_client("ws://localhost:8000/api/pubsub/subscribe")
    await client.wait_until_done()


async def websocket_skeleton():
    parking_place_id = 1
    level = 1
    websocket: websockets.WebSocketClientProtocol
    # initalize websocket connection to the server
    async with websockets.connect(
        "ws://localhost:8000/api/pubsub/subscribe",
    ) as websocket:
        # connected successfully
        print("Connected succesfully!\n")

        # Do a MQTT subscribe
        subscribe = {
            "request": {
                "method": "subscribe",
                "arguments": {"topics": [f"{parking_place_id}/{level}"]},
            },
        }
        await websocket.send(json.dumps(subscribe))
        print("Subscribing!\n")
        # A loop to receive and if needed send a received message to the server
        while True:
            # receive incoming message from the server
            message: dict
            message = json.loads(await websocket.recv())
            print(f"Received: {json.dumps(message, indent=2)}\n")
            # unpack the json message, get the request, data is in request.arguments.data
            request: dict = message.get("request")
            if request != None:
                # the request requires the app to send back a "received" message, send back the call_id
                notify = {
                    "response": {
                        "result": "None",
                        "result_type": "None",
                        "call_id": request.get("call_id"),
                    },
                }
                print(f"Sending: {json.dumps(notify, indent=2)}\n")
                await websocket.send(json.dumps(notify))


async def main():
    try:
        asyncio.create_task(websocket_skeleton())
        await asyncio.gather(*asyncio.all_tasks())
    except Exception as e:
        print(f"Exited nicely! Reason: {e}")


asyncio.run(main())
