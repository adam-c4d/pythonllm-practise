"""Call the running API: the health check, then 3 good diamonds and 1 bad one."""

import httpx

BASE_URL = "http://127.0.0.1:8002"

diamonds = [
    {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
     "depth": 61.5, "table": 56.0},
    {"carat": 1.0, "cut": "Premium", "color": "G", "clarity": "SI1",
     "depth": 62.0, "table": 58.0},
    {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1",
     "depth": 63.0, "table": 59.0},
    {"carat": 1.0, "cut": "Excellent", "color": "G", "clarity": "SI1",
     "depth": 62.0, "table": 58.0},
]

print(httpx.get(f"{BASE_URL}/health").json())
for diamond in diamonds:
    response = httpx.post(f"{BASE_URL}/predict", json=diamond)
    print(response.status_code, response.json())
