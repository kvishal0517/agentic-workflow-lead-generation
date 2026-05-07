import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger
from datetime import datetime

class GmailInterface:
    def __init__(self, token_path: str = 'token.json'):
        self.token_path = token_path
        self.creds = None
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path)

    def create_draft(self, to: str, subject: str, body_html: str, dry_run: bool = False):
        if not self.creds:
            logger.error("Gmail credentials not found. Run scripts/setup_oauth.py first.")
            return None

        if dry_run:
            logger.info(f"[DRY RUN] Would create Gmail draft for {to} with subject: {subject}")
            return "mock_draft_id"

        try:
            service = build('gmail', 'v1', credentials=self.creds)
            
            message = MIMEText(body_html, 'html')
            message['to'] = to
            message['subject'] = subject
            # Custom headers as per requirements
            message['X-Lead-Ref'] = f"LeadHunter-{datetime.now().strftime('%Y%m%d')}"
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            draft = service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            logger.info(f"Created draft {draft['id']} for {to}")
            return draft['id']
        except Exception as e:
            logger.error(f"Failed to create Gmail draft: {e}")
            return None

gmail = GmailInterface()
