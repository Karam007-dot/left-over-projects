import msal
import os
from dotenv import load_dotenv

# Load the keys from your .env file
load_dotenv()

def test_connection():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    tenant_id = os.getenv('TENANT_ID')
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    
    # Initialize the Microsoft Auth Guard
    app = msal.ConfidentialClientApplication(
        client_id, 
        authority=authority,
        client_credential=client_secret
    )

    # Request a "Token" (the VIP pass)
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in result:
        print("✅ SUCCESS: The bridge to Microsoft is OPEN!")
    else:
        print("❌ ERROR: Connection failed. Check your IDs and Secret.")
        print(f"Reason: {result.get('error_description')}")

if __name__ == "__main__":
    test_connection()