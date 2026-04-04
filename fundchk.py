import json, ssl, urllib.request, urllib.error

data = json.dumps({'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJaWkoxNzAzOF80NjhERjkyMUIxQTFBMDAyNDhCMjE1IiwicHVibGljS2V5IjoiNDY4ZGY5MjFiMWExYTAwMjQ4YjIxNSIsInVuaXF1ZUtleSI6Ik5ieE0wT3RHWnlpSndsTHc0aFdHTjErcFhFWTVUdzcreUZqTjdOYk5iTXQwSkV2dk5KVkFqWjdGSmRqOGdmYUwiLCJpc0ludGVyYWN0aXZlIjp0cnVlLCJpYXQiOjE3NzQ0MTczNTEsImV4cCI6MTc3NDUwMzc1MX0.u6g4izODavEKa-It3_l5drIWfoeOT4Ix1AV1M5h8JKc'}).encode()

req = urllib.request.Request(
    "https://smpb.jainam.in:4143/7hostlookup/user/balance?clientID=ZZJ17038",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.reason)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as e:
    print("ERROR:", e)