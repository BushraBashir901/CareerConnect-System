import secrets
import os
import requests
from app.core.security import create_jwt
from app.core.config import settings

# Environment variables
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
BACKEND_URL = settings.BACKEND_URL

# Temporary state store (replace with Redis for production)
state_store = {}

def generate_state(role: str) -> str:
    state = secrets.token_urlsafe(16)

    # store role with state
    state_store[state] = {
        "role": role
    }

    return state

def verify_state(state: str):
    if state not in state_store:
        return None   

    data = state_store[state]
    del state_store[state]

    return data

def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    """
    Exchange the authorization code from Google OAuth for an access token.
    
    Args:
        code (str): The authorization code received from Google.
        redirect_uri (str): The callback URL registered in Google OAuth.
    
    Returns:
        str: Access token string.
    
    Raises:
        requests.HTTPError: If the HTTP request fails.
    """
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data)
    r.raise_for_status()
    return r.json().get("access_token")

def get_user_info(access_token: str) -> dict:
    """
    Fetch the authenticated user's information from Google.
    
    Args:
        access_token (str): The OAuth access token.
    
    Returns:
        dict: User info returned by Google.
    
    Raises:
        requests.HTTPError: If the HTTP request fails.
    """
    r = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    r.raise_for_status()
    return r.json()

