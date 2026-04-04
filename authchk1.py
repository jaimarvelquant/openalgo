import json, ssl, urllib.request
data = json.dumps({"uniqueKey":"MKT7Ck0EhRzjk+Y5cG1AT8HELOrg409Dp/vN+NJVrhHtT6fVJzRu8FkjKydtTA04"}).encode()
req = urllib.request.Request(
    "https://smpb.jainam.in:4143/5hostlookup",
    data=data,
    headers={"Content-Type":"application/json"},
    method="POST",
)
print(urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()).read().decode())