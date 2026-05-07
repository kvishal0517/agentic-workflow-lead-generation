import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def setup_oauth():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.error("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
                return

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080')]
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Extract user info (optional, for confirmation)
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    
    logger.success(f"Successfully authenticated for: {profile['emailAddress']}")
    logger.info("Credentials saved to token.json")

if __name__ == '__main__':
    setup_oauth()
