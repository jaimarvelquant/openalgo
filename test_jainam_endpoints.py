#!/usr/bin/env python3
"""
Systematic testing of Jainam API endpoints to identify working authentication configuration.

This script tests all combinations of:
- Base URLs (HTTP/HTTPS, different servers/ports)
- Endpoint paths (/user/session, /interactive/user/session, /HostLookUp)
- Request payloads (with/without uniqueKey)

Results are saved to a CSV file for analysis.
"""

import os
import sys
import json
import httpx
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load credentials from .env
from dotenv import load_dotenv
load_dotenv()

INTERACTIVE_API_KEY = os.getenv('JAINAM_INTERACTIVE_API_KEY')
INTERACTIVE_API_SECRET = os.getenv('JAINAM_INTERACTIVE_API_SECRET')

# Test matrix
BASE_URLS = [
    "https://smpb.jainam.in:4143",
    "http://smpb.jainam.in:4143",
    "https://ctrade.jainam.in:4001",
    "http://ctrade.jainam.in:4001",
]

ENDPOINT_PATHS = [
    "/user/session",
    "/interactive/user/session",
    "/HostLookUp",
    "/hostlookup",
]

# Test payloads
def get_test_payloads():
    """Generate test payloads for different scenarios."""
    return {
        "direct_login": {
            "appKey": INTERACTIVE_API_KEY,
            "secretKey": INTERACTIVE_API_SECRET,
            "source": "WEBAPI"
        },
        "login_with_uniquekey": {
            "appKey": INTERACTIVE_API_KEY,
            "secretKey": INTERACTIVE_API_SECRET,
            "source": "WEBAPI",
            "uniqueKey": "test_unique_key"
        },
        "hostlookup": {
            "AccessPassword": "2021HostLookUpAccess",
            "version": "interactive_1.0.1"
        }
    }


def test_endpoint(base_url: str, endpoint_path: str, payload: Dict, payload_name: str) -> Dict:
    """
    Test a single endpoint with given payload.
    
    Returns:
        Dict with test results including status code, response, and analysis
    """
    full_url = f"{base_url}{endpoint_path}"
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "endpoint_path": endpoint_path,
        "full_url": full_url,
        "payload_type": payload_name,
        "http_method": "POST",
        "status_code": None,
        "response_type": None,
        "response_body": None,
        "error_message": None,
        "conclusion": None,
        "has_token": False,
        "has_connection_string": False,
    }
    
    try:
        # Make POST request with timeout
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.post(
                full_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            result["status_code"] = response.status_code
            
            # Try to parse as JSON
            try:
                json_response = response.json()
                result["response_type"] = "JSON"
                result["response_body"] = json.dumps(json_response, indent=2)
                
                # Check for success indicators
                if isinstance(json_response, dict):
                    result["has_token"] = "token" in str(json_response).lower()
                    result["has_connection_string"] = "connectionstring" in str(json_response).lower()
                    
                    # Extract error message if present
                    if "description" in json_response:
                        result["error_message"] = json_response["description"]
                    elif "message" in json_response:
                        result["error_message"] = json_response["message"]
                
                elif isinstance(json_response, list) and len(json_response) > 0:
                    first_item = json_response[0]
                    if isinstance(first_item, dict):
                        result["has_token"] = "token" in str(first_item).lower()
                        result["has_connection_string"] = "connectionstring" in str(first_item).lower()
                        
                        if "description" in first_item:
                            result["error_message"] = first_item["description"]
                        elif "message" in first_item:
                            result["error_message"] = first_item["message"]
                
            except Exception:
                # Not JSON, likely HTML error page
                result["response_type"] = "HTML/Text"
                result["response_body"] = response.text[:500]  # First 500 chars
                
                # Check for common error patterns
                if "404 Not Found" in response.text:
                    result["error_message"] = "404 Not Found - Endpoint does not exist"
                elif "400 Bad Request" in response.text:
                    result["error_message"] = "400 Bad Request"
                    if "HTTPS port" in response.text:
                        result["error_message"] += " - HTTP sent to HTTPS port"
            
            # Determine conclusion
            if result["status_code"] == 200:
                if result["has_token"]:
                    result["conclusion"] = "✅ SUCCESS - Authentication token received"
                elif result["has_connection_string"]:
                    result["conclusion"] = "✅ SUCCESS - HostLookUp connection string received"
                else:
                    result["conclusion"] = "⚠️ SUCCESS - But no token/connection string found"
            elif result["status_code"] == 404:
                result["conclusion"] = "❌ ENDPOINT NOT FOUND"
            elif result["status_code"] == 400:
                result["conclusion"] = "⚠️ ENDPOINT EXISTS - Bad request (check payload)"
            elif result["status_code"] == 401:
                result["conclusion"] = "⚠️ ENDPOINT EXISTS - Unauthorized (check credentials)"
            else:
                result["conclusion"] = f"❌ HTTP {result['status_code']}"
                
    except httpx.ConnectError as e:
        result["error_message"] = f"Connection error: {str(e)}"
        result["conclusion"] = "❌ CONNECTION FAILED"
    except httpx.TimeoutException:
        result["error_message"] = "Request timeout"
        result["conclusion"] = "❌ TIMEOUT"
    except Exception as e:
        result["error_message"] = f"Unexpected error: {str(e)}"
        result["conclusion"] = "❌ ERROR"
    
    return result


def run_all_tests() -> List[Dict]:
    """Run all test combinations and return results."""
    results = []
    payloads = get_test_payloads()
    
    total_tests = len(BASE_URLS) * len(ENDPOINT_PATHS) * len(payloads)
    current_test = 0
    
    print("=" * 80)
    print("JAINAM API ENDPOINT SYSTEMATIC TESTING")
    print("=" * 80)
    print(f"\nTotal test combinations: {total_tests}")
    print(f"Base URLs: {len(BASE_URLS)}")
    print(f"Endpoint paths: {len(ENDPOINT_PATHS)}")
    print(f"Payload types: {len(payloads)}")
    print("\nStarting tests...\n")
    
    for base_url in BASE_URLS:
        for endpoint_path in ENDPOINT_PATHS:
            for payload_name, payload in payloads.items():
                current_test += 1
                
                # Skip non-HostLookUp payloads for HostLookUp endpoints
                if "hostlookup" in endpoint_path.lower() and payload_name != "hostlookup":
                    continue
                
                # Skip HostLookUp payload for non-HostLookUp endpoints
                if "hostlookup" not in endpoint_path.lower() and payload_name == "hostlookup":
                    continue
                
                print(f"[{current_test}/{total_tests}] Testing: {base_url}{endpoint_path} ({payload_name})")
                
                result = test_endpoint(base_url, endpoint_path, payload, payload_name)
                results.append(result)
                
                # Print immediate result
                print(f"    Status: {result['status_code']} | {result['conclusion']}")
                if result['error_message']:
                    print(f"    Error: {result['error_message']}")
                print()
    
    return results


def save_results_to_csv(results: List[Dict], filename: str = "jainam_endpoint_test_results.csv"):
    """Save results to CSV file."""
    import csv
    
    if not results:
        print("No results to save")
        return
    
    # Get all keys from first result
    fieldnames = list(results[0].keys())
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Results saved to: {filename}")


def print_summary(results: List[Dict]):
    """Print summary of test results."""
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Count by conclusion
    conclusions = {}
    for result in results:
        conclusion = result['conclusion']
        conclusions[conclusion] = conclusions.get(conclusion, 0) + 1
    
    print("\nResults by conclusion:")
    for conclusion, count in sorted(conclusions.items()):
        print(f"  {conclusion}: {count}")
    
    # Find successful tests
    successful_tests = [r for r in results if r['status_code'] == 200]
    
    if successful_tests:
        print(f"\n✅ SUCCESSFUL TESTS ({len(successful_tests)}):")
        for result in successful_tests:
            print(f"\n  URL: {result['full_url']}")
            print(f"  Payload: {result['payload_type']}")
            print(f"  Conclusion: {result['conclusion']}")
            if result['has_token']:
                print(f"  ✅ Has authentication token!")
            if result['has_connection_string']:
                print(f"  ✅ Has connection string!")
    else:
        print("\n❌ NO SUCCESSFUL TESTS FOUND")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if not INTERACTIVE_API_KEY or not INTERACTIVE_API_SECRET:
        print("ERROR: JAINAM_INTERACTIVE_API_KEY and JAINAM_INTERACTIVE_API_SECRET must be set in .env")
        sys.exit(1)
    
    # Run all tests
    results = run_all_tests()
    
    # Save results
    save_results_to_csv(results)
    
    # Print summary
    print_summary(results)
    
    print("\n✅ Testing complete!")

