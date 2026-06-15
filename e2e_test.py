import asyncio
import requests
import websockets
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/ws"

def run_flow():
    session = requests.Session()
    
    print("1. Registering Driver")
    driver_data = {
        "email": f"driver_{time.time()}@example.com",
        "password": "StrongPassword123!",
        "role": "DRIVER",
        "first_name": "John",
        "last_name": "Doe"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=driver_data)
    print("Driver Register:", r.status_code, r.text)
    driver_id = r.json()["id"]

    print("2. Login Driver")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": driver_data["email"], "password": "StrongPassword123!"})
    print("Driver Login:", r.status_code)
    driver_token = r.json()["access_token"]

    print("3. Registering Passenger")
    passenger_data = {
        "email": f"passenger_{time.time()}@example.com",
        "password": "StrongPassword123!",
        "role": "CUSTOMER",
        "first_name": "Jane",
        "last_name": "Smith"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=passenger_data)
    print("Passenger Register:", r.status_code, r.text)
    passenger_id = r.json()["id"]

    print("4. Login Passenger")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": passenger_data["email"], "password": "StrongPassword123!"})
    print("Passenger Login:", r.status_code)
    passenger_token = r.json()["access_token"]

    print("5. Create Booking")
    from datetime import datetime, timezone
    booking_data = {
        "pickup_location": "123 Main St",
        "dropoff_location": "456 Market St",
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "service_type": "STANDARD"
    }
    r = session.post(
        f"{BASE_URL}/bookings", 
        json=booking_data,
        headers={"Authorization": f"Bearer {passenger_token}"}
    )
    print("Create Booking:", r.status_code, r.text)
    booking_id = r.json()["id"]

    print("6. Dispatch Booking")
    r = session.post(
        f"{BASE_URL}/dispatch/{booking_id}/start",
        headers={"Authorization": f"Bearer {passenger_token}"}
    )
    print("Dispatch:", r.status_code, r.text)

    async def ws_flow():
        print("7. Connecting Driver WebSocket")
        # Ensure we connect to the correct path, based on grep_search it's /drivers/{driver_id}
        ws_endpoint = f"{WS_URL}/drivers/{driver_id}?token={driver_token}"
        try:
            async with websockets.connect(ws_endpoint) as websocket:
                print("Driver Connected to WebSocket")
                location_update = {
                    "type": "location_update",
                    "data": {
                        "lat": 37.7750,
                        "lon": -122.4190
                    }
                }
                await websocket.send(json.dumps(location_update))
                print("Sent location update")
                
                # Wait briefly for Celery/RabbitMQ to process dispatch and potentially send a message back
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print("Received WS msg:", msg)
                except asyncio.TimeoutError:
                    print("No WS message received in 5s (expected if dispatch takes longer or async)")
        except Exception as e:
            print("WS Error:", e)

    asyncio.run(ws_flow())

    print("8. Driver Accepts Booking (Assign Driver)")
    r = session.patch(
        f"{BASE_URL}/bookings/{booking_id}/assign-driver",
        json={"driver_id": driver_id},
        headers={"Authorization": f"Bearer {driver_token}"}
    )
    print("Assign Driver:", r.status_code, r.text)
    
    print("Flow Complete")

if __name__ == "__main__":
    run_flow()
