import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "operator@airlynk.com", "password": "Admin123!"}
        )
        print("Status Code:", response.status_code)
        print("Response Body:", response.json())
        
        token = response.json().get("access_token")
        if token:
            me_res = await client.get("http://localhost:8000/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            print("Me Status:", me_res.status_code)
            print("Me Body:", me_res.json())

if __name__ == "__main__":
    asyncio.run(test_api())
