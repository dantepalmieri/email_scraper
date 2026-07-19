from auth_manager import build_gmail_service

# verify that the gmail service is working
gmail_service = build_gmail_service()
# get the profile of the authenticated user
profile = gmail_service.users().getProfile(userId='me').execute()


print(profile["emailAddress"])