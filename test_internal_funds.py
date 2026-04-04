import os
import sys

# Add project root to path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from services.funds_service import get_funds
from database.auth_db import get_auth_token
from database.apilog_db import init_db

app = Flask(__name__)
app.secret_key = "test"

with app.app_context():
    init_db()
    # Let's see who is the user
    from database.auth_db import get_user_id, Base, engine
    # We don't have request context, but we know the broker is jainamprop.
    # The first user with jainamprop is probably the one.
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    from database.auth_db import UserAuth
    user_auth = session.query(UserAuth).filter(UserAuth.broker == 'jainamprop', UserAuth.auth_token != '').first()
    
    if user_auth:
        username = user_auth.user_id # actually this is the app username
        print(f"Testing with username: {username}, broker: {user_auth.broker}")
        
        # Test get_funds
        success, response, status = get_funds(auth_token=user_auth.auth_token, broker='jainamprop')
        print(f"Success: {success}")
        print(f"Response: {response}")
        print(f"Status code: {status}")
    else:
        print("No jainamprop user with auth token found in database.")
