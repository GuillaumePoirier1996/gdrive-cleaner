import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from config import (
    CREDENTIALS_FILE,
    TOKEN_FILE,
    SCOPES
)

def authenticate_google_drive() -> Credentials:
    """
    Authenticate the user and retrieve Google Drive API credentials.

    Returns:
        Credentials: A valid set of credentials to access the Google Drive API.
    """
    creds = None

    # Load existing credentials if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds

def set_service() -> Resource:
    """
    Authenticate and create a Google Drive API service instance.

    Returns:
        Resource: A Google Drive v3 service object ready for API calls.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)
    return service
