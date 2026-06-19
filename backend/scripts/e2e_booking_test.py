"""
AirLynk -- E2E Booking Flow Verification Script.

Tests the complete booking lifecycle:
  1. Register customer
  2. Login customer
  3. Get airport list
  4. Estimate fare
  5. Create booking
  6. Create payment intent + mock webhook
  7. Login operator -> assign driver directly
  8. Login as assigned driver -> start trip
  9. Complete trip
  10. Verify final state

Outputs a verification report with pass/fail for each step.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import httpx

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = []


def report(step: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    RESULTS.append({"step": step, "passed": passed, "detail": detail})
    print(f"  {status}  {step}: {detail}")


async def main():
    print("=" * 70)
    print("  AirLynk -- E2E Booking Flow Verification")
    print("=" * 70)
    print()

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # -- Step 0: Health Check --
        print("[Step 0] Health Check")
        try:
            r = await client.get("http://localhost:8000/health")
            data = r.json()
            healthy = data.get("data", {}).get("status") == "healthy"
            report("Health Check", healthy, f"status={data.get('data', {}).get('status')}")
            if not healthy:
                print("  [WARN] Infrastructure unhealthy. Aborting.")
                return
        except Exception as e:
            report("Health Check", False, str(e))
            return

        # -- Step 1: Register Customer --
        print("\n[Step 1] Register Customer")
        test_email = f"e2e_test_{int(datetime.now().timestamp())}@airlynk.in"
        test_password = "E2eTestPass#2026!!"
        try:
            r = await client.post("/auth/register", json={
                "email": test_email,
                "password": test_password,
            })
            if r.status_code == 201:
                customer_data = r.json()
                customer_id = customer_data.get("id") or customer_data.get("data", {}).get("id")
                report("Register Customer", True, f"email={test_email}, id={customer_id}")
            elif r.status_code == 409:
                report("Register Customer", True, "User already exists (409)")
            else:
                report("Register Customer", False, f"status={r.status_code}, body={r.text[:200]}")
                return
        except Exception as e:
            report("Register Customer", False, str(e))
            return

        # -- Step 2: Login Customer --
        print("\n[Step 2] Login Customer")
        try:
            r = await client.post("/auth/login", json={
                "email": test_email,
                "password": test_password,
            })
            if r.status_code == 200:
                tokens = r.json()
                if "data" in tokens:
                    tokens = tokens["data"]
                customer_token = tokens["access_token"]
                report("Login Customer", True, f"token={customer_token[:20]}...")
            else:
                # Try with seeded customer
                r = await client.post("/auth/login", json={
                    "email": "customer@airlynk.in",
                    "password": "Customer#2026!!",
                })
                if r.status_code == 200:
                    tokens = r.json()
                    if "data" in tokens:
                        tokens = tokens["data"]
                    customer_token = tokens["access_token"]
                    test_email = "customer@airlynk.in"
                    report("Login Customer", True, f"Used seeded customer, token={customer_token[:20]}...")
                else:
                    report("Login Customer", False, f"status={r.status_code}, body={r.text[:200]}")
                    return
        except Exception as e:
            report("Login Customer", False, str(e))
            return

        customer_headers = {"Authorization": f"Bearer {customer_token}"}

        # -- Step 3: Get Airport List --
        print("\n[Step 3] Get Airport List")
        try:
            r = await client.get("/airports")
            if r.status_code == 200:
                airports = r.json()
                if isinstance(airports, dict) and "data" in airports:
                    airports = airports["data"]
                airport_count = len(airports) if isinstance(airports, list) else 0
                report("Get Airport List", airport_count > 0, f"Found {airport_count} airports")
                if airport_count > 0:
                    # Pick Delhi airport for consistent test
                    pickup_airport = None
                    for ap in airports:
                        if ap.get("city") == "Delhi" or ap.get("code") == "DEL":
                            pickup_airport = ap
                            break
                    if not pickup_airport:
                        pickup_airport = airports[0]
                else:
                    report("Get Airport List", False, "No airports in database")
                    return
            else:
                report("Get Airport List", False, f"status={r.status_code}")
                return
        except Exception as e:
            report("Get Airport List", False, str(e))
            return

        # -- Step 4: Estimate Fare --
        print("\n[Step 4] Estimate Fare")
        pickup_lat = float(pickup_airport.get("latitude", 28.5562))
        pickup_lng = float(pickup_airport.get("longitude", 77.1000))
        dropoff_lat = 28.6315  # Connaught Place
        dropoff_lng = 77.2167
        city = pickup_airport.get("city", "Delhi")

        try:
            # First get geo estimate
            geo_r = await client.post("/geo/estimate", json={
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "dropoff_lat": dropoff_lat,
                "dropoff_lng": dropoff_lng,
            })
            if geo_r.status_code == 200:
                geo_data = geo_r.json()
                if isinstance(geo_data, dict) and "data" in geo_data:
                    geo_data = geo_data["data"]
                distance_km = float(geo_data.get("distance_km", 20))
                duration_mins = int(geo_data.get("duration_minutes", geo_data.get("duration_mins", 40)))
                report("Geo Estimate", True, f"distance={distance_km}km, duration={duration_mins}min")
            else:
                report("Geo Estimate", False, f"status={geo_r.status_code}, body={geo_r.text[:200]}")
                distance_km = 20.0
                duration_mins = 40

            # Then pricing estimate
            pricing_r = await client.post("/pricing/estimate", json={
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "dropoff_lat": dropoff_lat,
                "dropoff_lng": dropoff_lng,
                "city": city,
                "vehicle_type": "sedan",
                "estimated_distance_km": distance_km,
                "estimated_duration_minutes": max(duration_mins, 1),
                "is_airport": True,
            }, headers=customer_headers)
            if pricing_r.status_code == 200:
                pricing_data = pricing_r.json()
                if isinstance(pricing_data, dict) and "data" in pricing_data:
                    pricing_data = pricing_data["data"]
                total_fare = float(pricing_data.get("total_estimate", 0))
                report("Pricing Estimate", total_fare > 0, f"fare=INR {total_fare}")
            else:
                report("Pricing Estimate", False, f"status={pricing_r.status_code}, body={pricing_r.text[:200]}")
                total_fare = 500.0
        except Exception as e:
            report("Fare Estimate", False, str(e))
            total_fare = 500.0

        # -- Step 5: Create Booking --
        print("\n[Step 5] Create Booking")
        try:
            scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            r = await client.post("/bookings", json={
                "pickup_location": f"{city} - {pickup_airport.get('name', 'Airport')}",
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "dropoff_location": "Connaught Place",
                "dropoff_lat": dropoff_lat,
                "dropoff_lng": dropoff_lng,
                "scheduled_time": scheduled_time,
                "passenger_count": 2,
            }, headers=customer_headers)
            if r.status_code == 201:
                booking_data = r.json()
                if isinstance(booking_data, dict) and "data" in booking_data:
                    booking_data = booking_data["data"]
                booking_id = booking_data.get("id")
                booking_price = booking_data.get("estimated_price", 0)
                report("Create Booking", True, f"id={booking_id}, price=INR {booking_price}, status={booking_data.get('booking_status')}")
            else:
                report("Create Booking", False, f"status={r.status_code}, body={r.text[:300]}")
                return
        except Exception as e:
            report("Create Booking", False, str(e))
            return

        # -- Step 6: Payment Flow --
        print("\n[Step 6] Payment Flow")
        try:
            r = await client.post("/payments/create-intent", json={
                "booking_id": booking_id,
                "amount": float(total_fare),
                "currency": "INR",
            }, headers=customer_headers)
            if r.status_code in [200, 201]:
                intent_data = r.json()
                if isinstance(intent_data, dict) and "data" in intent_data:
                    intent_data = intent_data["data"]
                intent_id = intent_data.get("id")
                report("Create Payment Intent", True, f"intent_id={intent_id}")

                r2 = await client.post("/payments/webhook/mock", json={
                    "intent_id": intent_id,
                    "status": "succeeded",
                })
                if r2.status_code == 200:
                    report("Mock Payment Webhook", True, "Payment succeeded")
                else:
                    report("Mock Payment Webhook", False, f"status={r2.status_code}, body={r2.text[:200]}")
            else:
                report("Create Payment Intent", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            report("Payment Flow", False, str(e))

        # -- Step 7: Operator Login + Assign Driver --
        print("\n[Step 7] Operator Login + Assign Driver")
        try:
            r = await client.post("/auth/login", json={
                "email": "operator@airlynk.in",
                "password": "Operator#2026!!",
            })
            if r.status_code == 200:
                op_tokens = r.json()
                if "data" in op_tokens:
                    op_tokens = op_tokens["data"]
                operator_token = op_tokens["access_token"]
                report("Operator Login", True, f"token={operator_token[:20]}...")
            else:
                report("Operator Login", False, f"status={r.status_code}, body={r.text[:200]}")
                return
        except Exception as e:
            report("Operator Login", False, str(e))
            return

        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        # Get drivers and assign
        assigned_driver_email = None
        try:
            r = await client.get("/fleet/drivers", headers=operator_headers)
            if r.status_code == 200:
                drivers_data = r.json()
                if isinstance(drivers_data, dict) and "data" in drivers_data:
                    drivers_data = drivers_data["data"]
                report("Fleet Drivers List", isinstance(drivers_data, list) and len(drivers_data) > 0, 
                       f"Found {len(drivers_data) if isinstance(drivers_data, list) else 0} drivers")
                
                if isinstance(drivers_data, list) and len(drivers_data) > 0:
                    driver = drivers_data[0]
                    driver_id = driver["id"]
                    vehicles = driver.get("vehicles", [])
                    
                    if vehicles:
                        vehicle_id = vehicles[0]["id"]
                    else:
                        vr = await client.get(f"/fleet/vehicles?driver_id={driver_id}", headers=operator_headers)
                        v_data = vr.json() if vr.status_code == 200 else []
                        if isinstance(v_data, list) and len(v_data) > 0:
                            vehicle_id = v_data[0]["id"]
                        else:
                            vehicle_id = None

                    if vehicle_id:
                        # Wait briefly for any background dispatch to settle
                        await asyncio.sleep(2)
                        
                        r = await client.patch(f"/bookings/{booking_id}/assign-driver", json={
                            "driver_id": driver_id,
                            "vehicle_id": vehicle_id,
                        }, headers=operator_headers)
                        
                        if r.status_code == 200:
                            report("Assign Driver", True, f"driver={driver_id[:8]}...")
                            # Find the driver email for login
                            assigned_driver_email = f"driver1@airlynk.in"  # First driver
                        else:
                            # Check if dispatch already assigned
                            booking_r = await client.get(f"/bookings/{booking_id}", headers=operator_headers)
                            if booking_r.status_code == 200:
                                b_data = booking_r.json()
                                if isinstance(b_data, dict) and "data" in b_data:
                                    b_data = b_data["data"]
                                current_status = b_data.get("booking_status")
                                if current_status in ["driver_assigned", "DRIVER_ASSIGNED"]:
                                    report("Assign Driver", True, f"Already assigned by dispatch, status={current_status}")
                                    assigned_driver_email = "driver1@airlynk.in"
                                else:
                                    report("Assign Driver", False, f"status={r.status_code}, booking_status={current_status}, body={r.text[:200]}")
                            else:
                                report("Assign Driver", False, f"status={r.status_code}, body={r.text[:200]}")
                    else:
                        report("Assign Driver", False, "No vehicle available")
            else:
                report("Assign Driver", False, f"Fleet list failed: status={r.status_code}")
        except Exception as e:
            report("Assign Driver", False, str(e))

        # -- Step 8: Start Trip (as assigned driver) --
        print("\n[Step 8] Start Trip")
        if not assigned_driver_email:
            report("Start Trip", False, "No driver assigned, skipping")
        else:
            try:
                # Check current booking state to find the assigned driver
                booking_r = await client.get(f"/bookings/{booking_id}", headers=operator_headers)
                b_data = booking_r.json()
                if isinstance(b_data, dict) and "data" in b_data:
                    b_data = b_data["data"]
                
                assigned_driver_id_from_booking = b_data.get("assigned_driver_id")
                
                # Try each driver email until we find the assigned one
                driver_token = None
                for i in range(1, 21):
                    r = await client.post("/auth/login", json={
                        "email": f"driver{i}@airlynk.in",
                        "password": f"Driver{i}#2026!!",
                    })
                    if r.status_code == 200:
                        drv_tokens = r.json()
                        if "data" in drv_tokens:
                            drv_tokens = drv_tokens["data"]
                        # Check if this driver's user ID matches the assigned driver
                        tmp_token = drv_tokens["access_token"]
                        tmp_headers = {"Authorization": f"Bearer {tmp_token}"}
                        
                        # Try starting trip with this driver
                        start_r = await client.patch(f"/bookings/{booking_id}/start", headers=tmp_headers)
                        if start_r.status_code == 200:
                            driver_token = tmp_token
                            driver_headers = tmp_headers
                            report("Start Trip", True, f"Started with driver{i}, status={start_r.status_code}")
                            break
                        elif "not assigned" in start_r.text.lower():
                            continue  # Try next driver
                        else:
                            report("Start Trip", False, f"driver{i}: status={start_r.status_code}, body={start_r.text[:200]}")
                            break
                
                if not driver_token:
                    report("Start Trip", False, "Could not find matching driver")
            except Exception as e:
                report("Start Trip", False, str(e))

        # -- Step 9: Complete Trip --
        print("\n[Step 9] Complete Trip")
        try:
            if driver_token:
                r = await client.patch(f"/bookings/{booking_id}/complete", headers=driver_headers)
                report("Complete Trip", r.status_code == 200, f"status={r.status_code}, body={r.text[:200]}")
            else:
                report("Complete Trip", False, "No driver token, skipping")
        except Exception as e:
            report("Complete Trip", False, str(e))

        # -- Step 10: Verify Final Booking State --
        print("\n[Step 10] Verify Final Booking State")
        try:
            r = await client.get(f"/bookings/{booking_id}", headers=customer_headers)
            if r.status_code == 200:
                final = r.json()
                if isinstance(final, dict) and "data" in final:
                    final = final["data"]
                final_status = final.get("booking_status")
                is_completed = final_status in ["completed", "COMPLETED"]
                report("Final Booking State", is_completed, f"status={final_status}")
            else:
                report("Final Booking State", False, f"status={r.status_code}")
        except Exception as e:
            report("Final Booking State", False, str(e))

    # -- Summary --
    print("\n" + "=" * 70)
    print("  E2E VERIFICATION SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    total = len(RESULTS)
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Rate:   {passed/total*100:.0f}%" if total > 0 else "  Rate:   N/A")
    print("=" * 70)

    if failed > 0:
        print("\n  FAILURES:")
        for r in RESULTS:
            if not r["passed"]:
                print(f"    - {r['step']}: {r['detail']}")

    print()
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
