import json, ssl, urllib.request, urllib.error

data = json.dumps({
    "secretKey": "Qhkx604$$n",
  "appKey": "468df921b1a1a00248b215",
  "uniqueKey": "NbxM0OtGZyiJwlLw4hWGN1+pXEY5Tw7+yFjN7NbNbMt0JEvvNJVAjZ7FJdj8gfaL"
}).encode()

req = urllib.request.Request(
    "https://smpb.jainam.in:4143/7hostlookup/user/session",
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