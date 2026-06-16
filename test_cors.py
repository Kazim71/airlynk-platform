import asyncio
import httpx

async def test_cors():
    async with httpx.AsyncClient() as client:
        response = await client.options(
            "http://localhost:8000/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:3002",
                "Access-Control-Request-Method": "POST"
            }
        )
        print("OPTIONS Status Code:", response.status_code)
        print("OPTIONS Headers:", dict(response.headers))

if __name__ == "__main__":
    asyncio.run(test_cors())
