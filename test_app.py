import asyncio
from backend.main import app
from starlette.requests import Request
from starlette.responses import Response

async def test_app():
    scope = {
        "type": "http",
        "method": "OPTIONS",
        "path": "/api/v1/auth/login",
        "headers": [
            (b"host", b"localhost:8000"),
            (b"origin", b"http://localhost:3002"),
            (b"access-control-request-method", b"POST"),
        ],
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
        "scheme": "http",
        "server": ("127.0.0.1", 8000),
    }

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        print("Response message:", message)

    try:
        await app(scope, receive, send)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_app())
