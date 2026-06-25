import requests

res = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "test422@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "role": "customer"
})
print("Status:", res.status_code)
print("Response:", res.text)
