# auth manager module for email scraper
# handles Google OAuth2 flow

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# readonly access
# modify added later once delete functionality is implemented
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# file locations for saved token and download client secret
TOKEN_FILE_PATH = "config/token.json"
CREDENTIALS_FILE_PATH = "config/client_secret.json"

# reads previously saved OAuth token from disk
# returns None if no saved token exists
def load_saved_credentials():
    # check if the token file exists
    if not os.path.exists(TOKEN_FILE_PATH):
        return None

    # load the saved credentials from the token file
    saved_credentials = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, GMAIL_SCOPES)

    return saved_credentials


# writes given OAuth credentials to disk as JSON for future runs
def save_credentials(credentials):
    # ensure the directory for the token file exists
    credentials_dir = os.path.dirname(TOKEN_FILE_PATH)

    # create the directory if it doesn't exist
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    # write the credentials to the token file
    with open(TOKEN_FILE_PATH, "w") as token_file:
        token_file.write(credentials.to_json())


# launches browser OAuth consent flow
# returns new credentials once user approves access
def run_oauth_flow():
    # create an OAuth flow object from the client secret file and the required scopes
    login_flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_PATH, GMAIL_SCOPES)

    # open a local web server and automatically handle the redirect
    new_credentials = login_flow.run_local_server(port=0)

    return new_credentials


# produces valid, ready-to-use OAuth credentials
def get_valid_credentials():
    credentials = load_saved_credentials()

    credentials_missing = credentials is None
    credentials_expired = False

    # check if credentials are expired only if they exist
    if not credentials_missing:
        credentials_expired = (credentials.expired and credentials.refresh_token is not None)

    # if credentials are missing or expired, run OAuth flow to get new credentials
    if credentials_missing:
        credentials = run_oauth_flow()
        save_credentials(credentials)
    elif credentials_expired:
        credentials.refresh(Request())
        save_credentials(credentials)

    return credentials


# builds and returns an authenticated Gmail API servcie object
def build_gmail_service():
    # get valid OAuth credentials
    credentials = get_valid_credentials()

    # build the Gmail API service object using the credentials
    gmail_service = build("gmail", "v1", credentials=credentials)

    return gmail_service