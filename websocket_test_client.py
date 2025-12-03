import asyncio
import json
import websockets
from datetime import datetime


async def test_cafe_websocket():
    token = "YOUR_JWT_TOKEN_HERE"
    cafe_id = "YOUR_CAFE_ID_HERE"

    uri = f"ws://localhost:8000/ws/cafe/{cafe_id}?token={token}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to cafe WebSocket")

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                print(f"\n📨 Received message:")
                print(f"Type: {data.get('type')}")
                print(f"Data: {json.dumps(data, indent=2)}")

                if data.get('type') == 'new_order':
                    print(f"\n🆕 NEW ORDER ALERT!")
                    print(f"Order ID: {data.get('order_id')}")
                    print(f"Customer: {data.get('customer_name')}")
                    print(f"Total: ${data.get('total_price')}")
                    print(f"Items: {data.get('items_count')}")

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_student_websocket():
    token = "YOUR_JWT_TOKEN_HERE"

    uri = f"ws://localhost:8000/ws/orders?token={token}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to orders WebSocket")

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                print(f"\n📨 Received message:")
                print(f"Type: {data.get('type')}")
                print(f"Data: {json.dumps(data, indent=2)}")

                if data.get('type') == 'order_status_update':
                    print(f"\n🔄 ORDER STATUS UPDATE!")
                    print(f"Order ID: {data.get('order_id')}")
                    print(f"New Status: {data.get('status')}")
                    print(f"Updated by: {data.get('updated_by')}")

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("WebSocket Test Client")
    print("=" * 50)
    print("1. Test Cafe WebSocket (for owners/workers)")
    print("2. Test Student WebSocket (for order updates)")
    print("=" * 50)

    choice = input("Enter choice (1 or 2): ")

    if choice == "1":
        asyncio.run(test_cafe_websocket())
    elif choice == "2":
        asyncio.run(test_student_websocket())
    else:
        print("Invalid choice")

