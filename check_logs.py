import os
import glob
import re

log_dir = r"D:\Github\openalgo\logs"
log_files = glob.glob(os.path.join(log_dir, "*.log"))

error_lines = []
for file in log_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'jainamprop' in line.lower() and ('error' in line.lower() or 'exception' in line.lower() or 'fail' in line.lower()):
                    error_lines.append(f"{os.path.basename(file)}: {line.strip()}")
                elif 'margin_data' in line.lower() or 'funds' in line.lower() or 'balance' in line.lower():
                    # capture funds fetching logs
                    if 'jainamprop' in line.lower() or 'funds.py' in line:
                        error_lines.append(f"{os.path.basename(file)}: {line.strip()}")
    except Exception:
        pass

# Print the last 100 relevant logs
for line in error_lines[-100:]:
    print(line)
