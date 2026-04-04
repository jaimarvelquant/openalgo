import urllib.request
import urllib.error
import ssl
import json

auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJaWkoxNzAzOF80NjhERjkyMUIxQTFBMDAyNDhCMjE1IiwicHVibGljS2V5IjoiNDY4ZGY5MjFiMWExYTAwMjQ4YjIxNSIsInVuaXF1ZUtleSI6Ik5ieE0wT3RHWnlpSndsTHc0aFdHTjErcFhFWTVUdzcreUZqTjdOYk5iTXQwSkV2dk5KVkFqWjdGSmRqOGdmYUwiLCJpc0ludGVyYWN0aXZlIjp0cnVlLCJpYXQiOjE3NzQ0MTczNTEsImV4cCI6MTc3NDUwMzc1MX0.u6g4izODavEKa-It3_l5drIWfoeOT4Ix1AV1M5h8JKc"
user_id = "ZZJ17038"
url = f"https://smpb.jainam.in:4143/7interactive/user/balance?clientID={user_id}"

req = urllib.request.Request(
    url,
    headers={
        "authorization": auth_token,
        "Content-Type": "application/json"
    },
    method="GET",
)

try:
    with urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()) as resp:
        data = resp.read().decode()
        print("SUCCESS:", data)
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.reason)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as e:
    print("ERROR:", e)
