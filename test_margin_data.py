import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Enable debug logging to see all steps
logging.basicConfig(level=logging.DEBUG)

import httpx

# Mock get_httpx_client to return HTTP/1.1 client
import utils.httpx_client
utils.httpx_client.get_httpx_client = lambda: httpx.Client(http2=False, http1=True, timeout=30.0)

from broker.jainamprop.api.funds import get_margin_data
from flask import Flask, session

app = Flask(__name__)
app.secret_key = "test"

# The token valid according to authchk2.py
auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJaWkoxNzAzOF80NjhERjkyMUIxQTFBMDAyNDhCMjE1IiwicHVibGljS2V5IjoiNDY4ZGY5MjFiMWExYTAwMjQ4YjIxNSIsInVuaXF1ZUtleSI6Ik5ieE0wT3RHWnlpSndsTHc0aFdHTjErcFhFWTVUdzcreUZqTjdOYk5iTXQwSkV2dk5KVkFqWjdGSmRqOGdmYUwiLCJpc0ludGVyYWN0aXZlIjp0cnVlLCJpYXQiOjE3NzQ0MTczNTEsImV4cCI6MTc3NDUwMzc1MX0.u6g4izODavEKa-It3_l5drIWfoeOT4Ix1AV1M5h8JKc"

with app.test_request_context():
    # Simulate JAINAMPROP_CLUSTER_BASE missing to trigger fallback
    # or simulate it present. Let's start with it missing.
    session["user"] = "admin"
    print("Testing get_margin_data...")
    try:
        data = get_margin_data(auth_token)
        print("Final output:", data)
    except Exception as e:
        print("Exception occurred:", e)
