from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000", "http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users = {}

@app.post("/api/v1/auth/register")
async def register(payload: dict):
    user_id = str(uuid.uuid4())
    users[payload["email"]] = {
        "id": user_id,
        "email": payload["email"],
        "is_active": True,
        "role": payload.get("role", "customer"),
        "created_at": datetime.now().isoformat()
    }
    return users[payload["email"]]

@app.post("/api/v1/auth/login")
async def login(payload: dict):
    email = payload["email"]
    if email not in users:
        role = "customer"
        if "operator" in email: role = "operator"
        elif "driver" in email: role = "driver"

        users[email] = {
            "id": str(uuid.uuid4()),
            "email": email,
            "is_active": True,
            "role": role,
            "created_at": datetime.now().isoformat()
        }
    return {
        "access_token": email,
        "refresh_token": "mock_refresh_" + email,
        "token_type": "bearer"
    }

@app.get("/api/v1/auth/me")
async def me(request: Request):
    auth_header = request.headers.get("Authorization")
    email = auth_header.replace("Bearer ", "") if auth_header else ""
    if email in users:
        return users[email]
    
    role = "customer"
    if "operator" in email: role = "operator"
    elif "driver" in email: role = "driver"

    return {
        "id": str(uuid.uuid4()),
        "email": email,
        "is_active": True,
        "role": role,
        "created_at": datetime.now().isoformat()
    }

# Mock bookings
bookings = []

@app.post("/api/v1/bookings")
async def create_booking(payload: dict):
    booking = {
        "id": str(uuid.uuid4()),
        "status": "pending",
        **payload
    }
    bookings.append(booking)
    return booking

@app.get("/api/v1/bookings")
async def get_bookings():
    return bookings

@app.patch("/api/v1/bookings/{booking_id}/assign")
async def assign_booking(booking_id: str, payload: dict):
    for b in bookings:
        if b["id"] == booking_id:
            b["driver_id"] = payload.get("driver_id")
            b["status"] = "assigned"
            return b
    return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
