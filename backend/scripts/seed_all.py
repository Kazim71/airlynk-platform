"""
AirLynk — Phase 2.5 Comprehensive Seed Script.

Seeds: 10 Airports, 10 Pricing Rules (per vehicle type), 20 Drivers,
       20 Vehicles, Roles, Users (operator, customer, driver accounts).

All data is Indian airport transfer data. No US/UK cities.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from backend.services.airports.models.airport import Airport
from backend.services.auth.models.user import Permission, Role, User
from backend.services.booking.models.booking import Booking, BookingStatus
from backend.services.fleet.models.fleet import Driver, Vehicle
from backend.services.pricing.models.pricing import PricingRule
from backend.shared.database.session import close_db, get_db_session, init_db
from backend.shared.security.password import hash_password

# ─── Indian Airports ──────────────────────────────────────────────
AIRPORTS = [
    {
        "code": "DEL",
        "name": "Indira Gandhi International Airport",
        "city": "Delhi",
        "lat": 28.5562,
        "lng": 77.1000,
    },
    {
        "code": "BOM",
        "name": "Chhatrapati Shivaji Maharaj International Airport",
        "city": "Mumbai",
        "lat": 19.0896,
        "lng": 72.8656,
    },
    {
        "code": "BLR",
        "name": "Kempegowda International Airport",
        "city": "Bengaluru",
        "lat": 13.1986,
        "lng": 77.7066,
    },
    {
        "code": "HYD",
        "name": "Rajiv Gandhi International Airport",
        "city": "Hyderabad",
        "lat": 17.2403,
        "lng": 78.4294,
    },
    {
        "code": "MAA",
        "name": "Chennai International Airport",
        "city": "Chennai",
        "lat": 12.9941,
        "lng": 80.1709,
    },
    {"code": "PNQ", "name": "Pune Airport", "city": "Pune", "lat": 18.5822, "lng": 73.9197},
    {
        "code": "CCU",
        "name": "Netaji Subhas Chandra Bose International Airport",
        "city": "Kolkata",
        "lat": 22.6547,
        "lng": 88.4467,
    },
    {
        "code": "AMD",
        "name": "Sardar Vallabhbhai Patel International Airport",
        "city": "Ahmedabad",
        "lat": 23.0772,
        "lng": 72.6347,
    },
    {
        "code": "GOI",
        "name": "Goa International Airport (Manohar Parrikar)",
        "city": "Goa",
        "lat": 15.3808,
        "lng": 73.8314,
    },
    {
        "code": "JAI",
        "name": "Jaipur International Airport",
        "city": "Jaipur",
        "lat": 26.8242,
        "lng": 75.8122,
    },
]

# ─── Indian Destinations (dropoff areas per city) ─────────────────
DESTINATIONS = {
    "Delhi": [
        {"name": "Connaught Place", "lat": 28.6315, "lng": 77.2167},
        {"name": "Noida Sector 62", "lat": 28.6270, "lng": 77.3650},
        {"name": "Gurugram Cyber Hub", "lat": 28.4945, "lng": 77.0889},
    ],
    "Mumbai": [
        {"name": "Bandra Kurla Complex", "lat": 19.0596, "lng": 72.8295},
        {"name": "Colaba", "lat": 18.9067, "lng": 72.8147},
        {"name": "Andheri West", "lat": 19.1364, "lng": 72.8296},
    ],
    "Bengaluru": [
        {"name": "Indiranagar", "lat": 12.9784, "lng": 77.6408},
        {"name": "Whitefield", "lat": 12.9698, "lng": 77.7500},
    ],
    "Hyderabad": [
        {"name": "Hitec City", "lat": 17.4435, "lng": 78.3772},
        {"name": "Banjara Hills", "lat": 17.4239, "lng": 78.4384},
    ],
    "Chennai": [
        {"name": "T Nagar", "lat": 13.0418, "lng": 80.2341},
        {"name": "OMR", "lat": 12.9674, "lng": 80.2589},
    ],
    "Pune": [
        {"name": "Koregaon Park", "lat": 18.5362, "lng": 73.8940},
        {"name": "Hinjewadi", "lat": 18.5912, "lng": 73.7390},
    ],
    "Kolkata": [
        {"name": "Park Street", "lat": 22.5526, "lng": 88.3520},
        {"name": "Salt Lake", "lat": 22.5958, "lng": 88.4136},
    ],
    "Ahmedabad": [
        {"name": "SG Highway", "lat": 23.0320, "lng": 72.5072},
        {"name": "Navrangpura", "lat": 23.0377, "lng": 72.5620},
    ],
    "Goa": [
        {"name": "Calangute", "lat": 15.5438, "lng": 73.7553},
        {"name": "Panjim", "lat": 15.4989, "lng": 73.8278},
    ],
    "Jaipur": [
        {"name": "MI Road", "lat": 26.9124, "lng": 75.7873},
        {"name": "Malviya Nagar", "lat": 26.8580, "lng": 75.8057},
    ],
}

# ─── Vehicle Types for Pricing ────────────────────────────────────
VEHICLE_TYPES = ["sedan", "suv", "luxury"]

# ─── Indian Driver Names ──────────────────────────────────────────
DRIVER_NAMES = [
    "Rajesh Kumar",
    "Anil Sharma",
    "Vikram Singh",
    "Suresh Patel",
    "Rahul Verma",
    "Deepak Gupta",
    "Manoj Tiwari",
    "Sanjay Yadav",
    "Ashok Joshi",
    "Prakash Nair",
    "Ramesh Chauhan",
    "Arvind Desai",
    "Nitin Patil",
    "Sachin Kulkarni",
    "Ajay Reddy",
    "Pradeep Menon",
    "Gaurav Mishra",
    "Rohit Kapoor",
    "Vivek Rathore",
    "Karan Malhotra",
]

# ─── Vehicle Makes/Models ────────────────────────────────────────
VEHICLES = [
    ("Maruti", "Ciaz"),
    ("Maruti", "Ertiga"),
    ("Hyundai", "Verna"),
    ("Hyundai", "Creta"),
    ("Tata", "Nexon"),
    ("Tata", "Harrier"),
    ("Toyota", "Innova Crysta"),
    ("Toyota", "Fortuner"),
    ("Mahindra", "XUV700"),
    ("Mahindra", "Thar"),
    ("Kia", "Seltos"),
    ("Kia", "Carens"),
    ("Honda", "City"),
    ("Honda", "Amaze"),
    ("Skoda", "Slavia"),
    ("MG", "Hector"),
    ("Tata", "Safari"),
    ("Hyundai", "Alcazar"),
    ("Mercedes-Benz", "E-Class"),
    ("BMW", "5 Series"),
]

# ─── Indian License Plates ───────────────────────────────────────
PLATES = [
    "DL01AB1234",
    "DL02CD5678",
    "MH01EF9012",
    "MH02GH3456",
    "KA01IJ7890",
    "KA02KL1234",
    "TN01MN5678",
    "TN02OP9012",
    "AP01QR3456",
    "AP02ST7890",
    "RJ01UV1234",
    "RJ02WX5678",
    "GJ01YZ9012",
    "GJ02AB3456",
    "WB01CD7890",
    "WB02EF1234",
    "GA01GH5678",
    "GA02IJ9012",
    "HR01KL3456",
    "UP01MN7890",
]


async def seed():
    await init_db()
    async for session in get_db_session():
        try:
            print("=" * 60)
            print("  AirLynk Phase 2.5 — Comprehensive Seed")
            print("=" * 60)

            # ── 1. Create Roles & Permissions ─────────────────────
            print("\n[1/7] Creating roles and permissions...")
            role_names = ["customer", "driver", "operator", "security_admin", "platform_admin"]
            roles = {}
            for name in role_names:
                existing = (
                    await session.execute(select(Role).where(Role.name == name))
                ).scalar_one_or_none()
                if existing:
                    roles[name] = existing
                    print(f"  Role '{name}' already exists.")
                else:
                    role = Role(name=name)
                    session.add(role)
                    await session.flush()
                    roles[name] = role
                    print(f"  Role '{name}' created.")

            # Basic permissions
            perm_names = [
                "booking:create",
                "booking:read",
                "booking:cancel",
                "fleet:manage",
                "dispatch:manage",
                "pricing:manage",
                "admin:all",
            ]
            for pname in perm_names:
                existing = (
                    await session.execute(select(Permission).where(Permission.name == pname))
                ).scalar_one_or_none()
                if not existing:
                    perm = Permission(name=pname)
                    session.add(perm)
            await session.flush()

            # ── 2. Create Test Users ──────────────────────────────
            print("\n[2/7] Creating test users...")

            test_users = {}
            user_defs = [
                ("operator@airlynk.in", "Operator#2026!!", "operator"),
                ("customer@airlynk.in", "Customer#2026!!", "customer"),
                ("admin@airlynk.in", "PlatAdmin#2026!!", "platform_admin"),
            ]
            # Add 20 driver users
            for i in range(20):
                user_defs.append((f"driver{i + 1}@airlynk.in", f"Driver{i + 1}#2026!!", "driver"))

            for email, password, role_name in user_defs:
                existing = (
                    await session.execute(select(User).where(User.email == email))
                ).scalar_one_or_none()
                if existing:
                    test_users[email] = existing
                    print(f"  User '{email}' already exists.")
                else:
                    user = User(
                        email=email,
                        hashed_password=hash_password(password),
                        role_id=roles[role_name].id,
                        is_active=True,
                    )
                    session.add(user)
                    await session.flush()
                    test_users[email] = user
                    print(f"  User '{email}' created with role '{role_name}'.")

            # ── 3. Seed Airports ──────────────────────────────────
            print("\n[3/7] Seeding 10 Indian airports...")
            airport_objs = {}
            for ap in AIRPORTS:
                existing = (
                    await session.execute(select(Airport).where(Airport.code == ap["code"]))
                ).scalar_one_or_none()
                if existing:
                    airport_objs[ap["code"]] = existing
                    print(f"  Airport {ap['code']} already exists.")
                else:
                    airport = Airport(
                        code=ap["code"],
                        name=ap["name"],
                        city=ap["city"],
                        latitude=ap["lat"],
                        longitude=ap["lng"],
                        timezone="Asia/Kolkata",
                    )
                    session.add(airport)
                    await session.flush()
                    airport_objs[ap["code"]] = airport
                    print(f"  Airport {ap['code']} ({ap['city']}) created.")

            # ── 4. Seed Pricing Rules ─────────────────────────────
            print("\n[4/7] Seeding pricing rules (10 cities × 3 vehicle types)...")
            pricing_configs = {
                "sedan": {
                    "base": 150,
                    "per_km": 14,
                    "per_min": 2,
                    "min_fare": 300,
                    "airport": 100,
                },
                "suv": {"base": 250, "per_km": 18, "per_min": 3, "min_fare": 450, "airport": 150},
                "luxury": {
                    "base": 500,
                    "per_km": 28,
                    "per_min": 5,
                    "min_fare": 800,
                    "airport": 250,
                },
            }
            for ap in AIRPORTS:
                for vtype, config in pricing_configs.items():
                    existing = (
                        await session.execute(
                            select(PricingRule).where(
                                PricingRule.city == ap["city"], PricingRule.vehicle_type == vtype
                            )
                        )
                    ).scalar_one_or_none()
                    if existing:
                        continue
                    rule = PricingRule(
                        city=ap["city"],
                        vehicle_type=vtype,
                        base_fare=Decimal(str(config["base"])),
                        per_km_rate=Decimal(str(config["per_km"])),
                        per_minute_rate=Decimal(str(config["per_min"])),
                        minimum_fare=Decimal(str(config["min_fare"])),
                        waiting_charge_per_minute=Decimal("3.00"),
                        cancellation_fee=Decimal("100.00"),
                        surge_multiplier=Decimal("1.00"),
                        airport_fee=Decimal(str(config["airport"])),
                        active=True,
                    )
                    session.add(rule)
            await session.flush()
            print(
                f"  Pricing rules created for {len(AIRPORTS)} cities × {len(pricing_configs)} vehicle types."
            )

            # ── 5. Seed 20 Drivers + 20 Vehicles ─────────────────
            print("\n[5/7] Seeding 20 drivers and 20 vehicles...")
            driver_objs = []
            for i in range(20):
                email = f"driver{i + 1}@airlynk.in"
                user = test_users[email]
                existing = (
                    await session.execute(select(Driver).where(Driver.user_id == user.id))
                ).scalar_one_or_none()
                if existing:
                    driver_objs.append(existing)
                    print(f"  Driver '{DRIVER_NAMES[i]}' already exists.")
                    continue

                driver = Driver(
                    user_id=user.id,
                    license_number=f"DL-{2024 + i}-{100000 + i:06d}",
                    is_active=True,
                    is_available=(i < 10),  # First 10 drivers are available
                )
                session.add(driver)
                await session.flush()
                driver_objs.append(driver)

                # Create vehicle for this driver
                make, model = VEHICLES[i]
                vehicle = Vehicle(
                    driver_id=driver.id,
                    make=make,
                    model=model,
                    license_plate=PLATES[i],
                )
                session.add(vehicle)
                print(f"  Driver '{DRIVER_NAMES[i]}' + {make} {model} ({PLATES[i]}) created.")
            await session.flush()

            # ── 6. Seed 50 Bookings ──────────────────────────────
            print("\n[6/7] Seeding 50 bookings...")
            customer = test_users["customer@airlynk.in"]
            booking_count = 0

            for i in range(50):
                ap_data = AIRPORTS[i % len(AIRPORTS)]
                city = ap_data["city"]
                dests = DESTINATIONS.get(
                    city,
                    [
                        {
                            "name": "City Center",
                            "lat": ap_data["lat"] + 0.05,
                            "lng": ap_data["lng"] + 0.05,
                        }
                    ],
                )
                dest = dests[i % len(dests)]

                # Vary statuses
                statuses = [
                    BookingStatus.CREATED,
                    BookingStatus.CONFIRMED,
                    BookingStatus.PAYMENT_AUTHORIZED,
                    BookingStatus.DISPATCHING,
                    BookingStatus.DRIVER_ASSIGNED,
                    BookingStatus.COMPLETED,
                    BookingStatus.COMPLETED,
                    BookingStatus.COMPLETED,
                    BookingStatus.CANCELLED,
                    BookingStatus.IN_PROGRESS,
                ]
                status = statuses[i % len(statuses)]

                assigned_driver = (
                    driver_objs[i % 20]
                    if status
                    in [
                        BookingStatus.DRIVER_ASSIGNED,
                        BookingStatus.IN_PROGRESS,
                        BookingStatus.COMPLETED,
                    ]
                    else None
                )

                # Get vehicle for assigned driver
                vehicle_id = None
                if assigned_driver:
                    vehicle_result = await session.execute(
                        select(Vehicle).where(Vehicle.driver_id == assigned_driver.id).limit(1)
                    )
                    vehicle = vehicle_result.scalar_one_or_none()
                    vehicle_id = vehicle.id if vehicle else None

                booking = Booking(
                    customer_id=customer.id,
                    pickup_location=f"{city} - {ap_data['name']}",
                    pickup_lat=ap_data["lat"],
                    pickup_lng=ap_data["lng"],
                    dropoff_location=dest["name"],
                    dropoff_lat=dest["lat"],
                    dropoff_lng=dest["lng"],
                    scheduled_time=datetime.now(UTC) + timedelta(hours=i + 1),
                    passenger_count=(i % 4) + 1,
                    booking_status=status,
                    estimated_price=float(Decimal(str(300 + (i * 47) % 2000))),
                    assigned_driver_id=assigned_driver.id if assigned_driver else None,
                    vehicle_id=vehicle_id,
                )
                session.add(booking)
                booking_count += 1

            await session.flush()
            print(f"  {booking_count} bookings created across {len(AIRPORTS)} cities.")

            # ── 7. Summary ────────────────────────────────────────
            await session.commit()
            print("\n" + "=" * 60)
            print("  ✅ SEED COMPLETE")
            print("=" * 60)
            print(f"  Roles:          {len(role_names)}")
            print(f"  Users:          {len(test_users)}")
            print(f"  Airports:       {len(AIRPORTS)}")
            print(f"  Pricing Rules:  {len(AIRPORTS) * len(pricing_configs)}")
            print("  Drivers:        20")
            print("  Vehicles:       20")
            print(f"  Bookings:       {booking_count}")
            print("=" * 60)
            print("\n  Test Credentials:")
            print("  ──────────────────")
            print("  Operator:  operator@airlynk.in / Operator#2026!!")
            print("  Customer:  customer@airlynk.in / Customer#2026!!")
            print("  Admin:     admin@airlynk.in    / PlatAdmin#2026!!")
            print("  Driver 1:  driver1@airlynk.in  / Driver1#2026!!")
            print()

        except Exception as e:
            print(f"\n❌ SEED FAILED: {e}")
            import traceback

            traceback.print_exc()
            await session.rollback()
            raise
        break

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
