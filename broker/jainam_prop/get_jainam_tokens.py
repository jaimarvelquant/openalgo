#!/usr/bin/env python3
"""
Jainam Prop Token Generator

This script obtains interactive and market data tokens from the Jainam XTS API
using direct login (no OAuth/request token needed).

Usage:
    python broker/jainam_prop/get_jainam_tokens.py

Features:
    - Reads credentials from .env file
    - Calls both Interactive and Market Data login APIs
    - Displays tokens with expiry information
    - Optionally saves tokens to .env file
    - Comprehensive error handling and validation

Author: MarvelQuant Team
Date: October 8, 2025
"""

import os
import sys
import json
import httpx
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from broker.jainam_prop.api.config import get_jainam_base_url


class JainamTokenGenerator:
    """Generate Jainam XTS API tokens"""
    
    def __init__(self):
        """Initialize with credentials from environment"""
        self.base_url = get_jainam_base_url()
        self.interactive_api_key = os.getenv('JAINAM_INTERACTIVE_API_KEY')
        self.interactive_api_secret = os.getenv('JAINAM_INTERACTIVE_API_SECRET')
        self.market_api_key = os.getenv('JAINAM_MARKET_API_KEY')
        self.market_api_secret = os.getenv('JAINAM_MARKET_API_SECRET')
        self.source = "WEBAPI"
        
        # Validate credentials
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that all required credentials are present"""
        missing = []
        
        if not self.interactive_api_key:
            missing.append('JAINAM_INTERACTIVE_API_KEY')
        if not self.interactive_api_secret:
            missing.append('JAINAM_INTERACTIVE_API_SECRET')
        if not self.market_api_key:
            missing.append('JAINAM_MARKET_API_KEY')
        if not self.market_api_secret:
            missing.append('JAINAM_MARKET_API_SECRET')
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please ensure these are set in your .env file."
            )
    
    def login_interactive(self):
        """
        Login to Interactive API
        
        Returns:
            dict: {
                'token': str,
                'user_id': str,
                'is_investor_client': bool
            }
        
        Raises:
            Exception: If login fails
        """
        url = f"{self.base_url}/interactive/user/session"
        
        payload = {
            "appKey": self.interactive_api_key,
            "secretKey": self.interactive_api_secret,
            "source": self.source
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"🔐 Logging in to Interactive API...")
        print(f"   URL: {url}")
        print(f"   App Key: {self.interactive_api_key[:10]}...")
        
        try:
            client = httpx.Client(timeout=30.0)
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('type') == 'success':
                result = data.get('result', {})
                token = result.get('token')
                user_id = result.get('userID')
                is_investor = result.get('isInvestorClient', False)
                
                print(f"✅ Interactive login successful!")
                print(f"   User ID: {user_id}")
                print(f"   Is Investor Client: {is_investor}")
                print(f"   Token: {token[:50]}...")
                
                return {
                    'token': token,
                    'user_id': user_id,
                    'is_investor_client': is_investor
                }
            else:
                error_msg = data.get('description', 'Unknown error')
                error_code = data.get('code', 'N/A')
                raise Exception(f"Interactive login failed [{error_code}]: {error_msg}")
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error during interactive login: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Network error during interactive login: {str(e)}")
        except Exception as e:
            raise Exception(f"Interactive login failed: {str(e)}")
    
    def login_market_data(self):
        """
        Login to Market Data API
        
        Returns:
            dict: {
                'token': str,
                'user_id': str
            }
        
        Raises:
            Exception: If login fails
        """
        payload = {
            "appKey": self.market_api_key,
            "secretKey": self.market_api_secret,
            "source": self.source
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        candidate_paths = [
            "/apimarketdata/auth/login",
            "/marketdata/auth/login",
            "/apibinarymarketdata/auth/login",
        ]
        
        last_error = None
        client = httpx.Client(timeout=30.0)
        
        print(f"\n🔐 Logging in to Market Data API...")
        
        for path in candidate_paths:
            url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
            print(f"   Trying URL: {url}")
            
            try:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('type') == 'success':
                    result = data.get('result', {})
                    token = result.get('token')
                    user_id = result.get('userID')
                    
                    print(f"✅ Market Data login successful!")
                    print(f"   User ID: {user_id}")
                    print(f"   Token: {token[:50]}...")
                    
                    return {
                        'token': token,
                        'user_id': user_id
                    }
                else:
                    error_msg = data.get('description', 'Unknown error')
                    error_code = data.get('code', 'N/A')
                    raise Exception(f"Market Data login failed [{error_code}]: {error_msg}")
            
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                body = e.response.text
                last_error = f"HTTP {status} - {body}"
                if status == 400 and "only enabled for CTCL" in body:
                    # Try next variant (binary market data)
                    continue
                if status != 404:
                    break  # Non-404 errors shouldn't fall through to alternate paths
            except httpx.RequestError as e:
                last_error = f"Network error: {str(e)}"
                break
            except Exception as e:
                last_error = str(e)
                break
        
        raise Exception(f"Market Data login failed: {last_error or 'Unknown error'}")
    
    def generate_tokens(self):
        """
        Generate both interactive and market data tokens
        
        Returns:
            dict: {
                'interactive_token': str,
                'market_token': str,
                'user_id': str,
                'is_investor_client': bool,
                'generated_at': str
            }
        """
        print("=" * 80)
        print("JAINAM PROP TOKEN GENERATOR")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Source: {self.source}")
        print("")
        
        # Login to Interactive API
        interactive_result = self.login_interactive()
        
        # Login to Market Data API
        market_result = self.login_market_data()
        
        # Combine results
        tokens = {
            'interactive_token': interactive_result['token'],
            'market_token': market_result['token'],
            'user_id': interactive_result['user_id'],
            'is_investor_client': interactive_result['is_investor_client'],
            'generated_at': datetime.now().isoformat()
        }
        
        return tokens
    
    def display_tokens(self, tokens):
        """Display tokens in a formatted way"""
        print("\n" + "=" * 80)
        print("✅ TOKENS GENERATED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nGenerated at: {tokens['generated_at']}")
        print(f"User ID: {tokens['user_id']}")
        print(f"Is Investor Client: {tokens['is_investor_client']}")
        print(f"\nEstimated expiry: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}")
        print("(Tokens typically valid for 24 hours - check Jainam API docs for exact duration)")
        
        print("\n" + "-" * 80)
        print("INTERACTIVE TOKEN (for orders, portfolio, positions):")
        print("-" * 80)
        print(tokens['interactive_token'])
        
        print("\n" + "-" * 80)
        print("MARKET DATA TOKEN (for quotes, historical data, depth):")
        print("-" * 80)
        print(tokens['market_token'])
        
        print("\n" + "=" * 80)
        print("COPY TO .ENV FILE")
        print("=" * 80)
        print("\nAdd these lines to your .env file:")
        print("")
        print(f"JAINAM_INTERACTIVE_SESSION_TOKEN={tokens['interactive_token']}")
        print(f"JAINAM_MARKET_TOKEN={tokens['market_token']}")
        print(f"JAINAM_USER_ID={tokens['user_id']}")
        print("")
    
    def save_to_env(self, tokens):
        """
        Save tokens to .env file
        
        Args:
            tokens (dict): Token data
        
        Returns:
            bool: True if saved successfully
        """
        env_file = project_root / '.env'
        
        if not env_file.exists():
            print(f"❌ .env file not found at {env_file}")
            return False
        
        # Read current .env content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Remove existing token lines
        new_lines = []
        for line in lines:
            if not any(line.startswith(prefix) for prefix in [
                'JAINAM_INTERACTIVE_SESSION_TOKEN=',
                'JAINAM_MARKET_TOKEN=',
                'JAINAM_USER_ID='
            ]):
                new_lines.append(line)
        
        # Add new tokens at the end
        if not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        
        new_lines.append('\n')
        new_lines.append('# Jainam Session Tokens (Generated by get_jainam_tokens.py)\n')
        new_lines.append(f'# Generated at: {tokens["generated_at"]}\n')
        new_lines.append(f'JAINAM_INTERACTIVE_SESSION_TOKEN={tokens["interactive_token"]}\n')
        new_lines.append(f'JAINAM_MARKET_TOKEN={tokens["market_token"]}\n')
        new_lines.append(f'JAINAM_USER_ID={tokens["user_id"]}\n')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Tokens saved to {env_file}")
        return True


def main():
    """Main function"""
    try:
        # Generate tokens
        generator = JainamTokenGenerator()
        tokens = generator.generate_tokens()
        
        # Display tokens
        generator.display_tokens(tokens)
        
        # Ask if user wants to save to .env
        print("\n" + "=" * 80)
        response = input("Do you want to save these tokens to .env file? (y/n): ").strip().lower()
        
        if response == 'y':
            generator.save_to_env(tokens)
            print("\n✅ Done! You can now run live API tests.")
        else:
            print("\n⚠️  Tokens not saved. Copy them manually to .env if needed.")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("1. Tokens are now ready for use")
        print("2. Run live validation scripts:")
        print("   python broker/jainam_prop/test_live_api.py")
        print("3. Tokens typically expire after 24 hours")
        print("4. Re-run this script to refresh tokens when needed")
        print("")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
