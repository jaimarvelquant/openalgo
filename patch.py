import sys
file_path = r"d:\Github\openalgo\broker\jainamprop\api\order_api.py"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    data = data.replace('    client_id = os.getenv("JAINAMPROP_USER_ID")', '    client_id = None', 1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)
    print("Patch applied successfully.")
except Exception as e:
    print(f"Error: {e}")
