import asyncio
import requests
import websockets
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/ws"

def run_flow():
    session = requests.Session()
    
    # ---- 1. Register & Login Operator ----
    print("1. Registering Operator")
    operator_data = {
        "email": f"operator_{time.time()}@example.com",
        "password": "StrongPassword123!",
        "role": "operator",
    }
    r = session.post(f"{BASE_URL}/auth/register", json=operator_data)
    print("Operator Register:", r.status_code, r.text)
    assert r.status_code == 201, f"Operator registration failed: {r.text}"
    operator_id = r.json()["id"]

    r = session.post(f"{BASE_URL}/auth/login", json={"email": operator_data["email"], "password": "StrongPassword123!"})
    print("Operator Login:", r.status_code)
    assert r.status_code == 200, f"Operator login failed: {r.text}"
    operator_token = r.json()["access_token"]

    # ---- 2. Register & Login Driver ----
    print("2. Registering Driver")
    driver_data = {
        "email": f"driver_{time.time()}@example.com",
        "password": "StrongPassword123!",
        "role": "driver",
        "first_name": "John",
        "last_name": "Doe"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=driver_data)
    print("Driver Register:", r.status_code, r.text)
    assert r.status_code == 201, f"Driver registration failed: {r.text}"
    driver_user_id = r.json()["id"]

    print("3. Login Driver")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": driver_data["email"], "password": "StrongPassword123!"})
    print("Driver Login:", r.status_code)
    assert r.status_code == 200, f"Driver login failed: {r.text}"
    driver_token = r.json()["access_token"]

    # ---- 3. Create Fleet Driver & Vehicle (as operator) ----
    print("4. Creating Fleet Driver Profile")
    r = session.post(f"{BASE_URL}/fleet/drivers", json={
        "user_id": driver_user_id,
        "license_number": f"LIC-{int(time.time())}",
        "is_active": True,
        "is_available": True,
    }, headers={"Authorization": f"Bearer {operator_token}"})
    print("Create Fleet Driver:", r.status_code, r.text)
    assert r.status_code == 201, f"Fleet driver creation failed: {r.text}"
    fleet_driver = r.json()
    fleet_driver_id = fleet_driver["id"]

    print("5. Creating Vehicle")
    r = session.post(f"{BASE_URL}/fleet/vehicles", json={
        "driver_id": fleet_driver_id,
        "make": "Toyota",
        "model": "Camry",
        "license_plate": f"DL-{int(time.time())}",
    }, headers={"Authorization": f"Bearer {operator_token}"})
    print("Create Vehicle:", r.status_code, r.text)
    assert r.status_code == 201, f"Vehicle creation failed: {r.text}"
    vehicle = r.json()
    vehicle_id = vehicle["id"]

    # ---- 4. Register & Login Passenger ----
    print("6. Registering Passenger")
    passenger_data = {
        "email": f"passenger_{time.time()}@example.com",
        "password": "StrongPassword123!",
        "role": "customer",
        "first_name": "Jane",
        "last_name": "Smith"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=passenger_data)
    print("Passenger Register:", r.status_code, r.text)
    assert r.status_code == 201, f"Passenger registration failed: {r.text}"
    passenger_id = r.json()["id"]

    print("7. Login Passenger")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": passenger_data["email"], "password": "StrongPassword123!"})
    print("Passenger Login:", r.status_code)
    assert r.status_code == 200, f"Passenger login failed: {r.text}"
    passenger_token = r.json()["access_token"]

    # ---- 5. Create Booking (as passenger) ----
    print("8. Create Booking")
    from datetime import datetime, timezone
    booking_data = {
        "pickup_location": "123 Main St",
        "pickup_lat": 28.6139,
        "pickup_lng": 77.2090,
        "dropoff_location": "456 Market St",
        "dropoff_lat": 28.5355,
        "dropoff_lng": 77.3910,
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "passenger_count": 1
    }
    r = session.post(
        f"{BASE_URL}/bookings", 
        json=booking_data,
        headers={"Authorization": f"Bearer {passenger_token}"}
    )
    print("Create Booking:", r.status_code, r.text)
    assert r.status_code == 201, f"Booking creation failed: {r.text}"
    booking_id = r.json()["id"]

    # ---- 6. Dispatch Booking (as operator) ----
    print("9. Dispatch Booking")
    r = session.post(
        f"{BASE_URL}/dispatch/{booking_id}/start",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    print("Dispatch:", r.status_code, r.text)
    assert r.status_code == 202, f"Dispatch failed: {r.text}"

    # ---- 7. Driver WebSocket Connection ----
    async def ws_flow():
        print("10. Connecting Driver WebSocket")
        ws_endpoint = f"{WS_URL}/drivers/{driver_user_id}?token={driver_token}"
        try:
            async with websockets.connect(ws_endpoint) as websocket:
                print("Driver Connected to WebSocket")
                location_update = {
                    "type": "location_update",
                    "data": {
                        "lat": 28.6139,
                        "lon": 77.2090
                    }
                }
                await websocket.send(json.dumps(location_update))
                print("Sent location update")
                
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print("Received WS msg:", msg)
                except asyncio.TimeoutError:
                    print("No WS message received in 5s (expected if dispatch takes longer or async)")
        except Exception as e:
            print("WS Error:", e)

    asyncio.run(ws_flow())

    # ---- 8. Assign Driver to Booking (as operator) ----
    print("11. Assign Driver to Booking")
    r = session.patch(
        f"{BASE_URL}/bookings/{booking_id}/assign-driver",
        json={"driver_id": fleet_driver_id, "vehicle_id": vehicle_id},
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    print("Assign Driver:", r.status_code, r.text)
    assert r.status_code == 200, f"Assign driver failed: {r.text}"
    
    print("\n=== E2E Flow Complete ===")

if __name__ == "__main__":
    run_flow()
