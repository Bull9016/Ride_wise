import requests
import json

payload = {
    "role": "Support Agent",
    "message": "Hello",
    "history": [],
    "mobile_number": None,
    "customer_id": None
}

try:
    print("Sending POST request to http://localhost:8001/api/chat")
    res = requests.post("http://localhost:8001/api/chat", json=payload)
    print("Status Code:", res.status_code)
    print("Response JSON:", res.json())
except Exception as e:
    print("Error:", str(e))
