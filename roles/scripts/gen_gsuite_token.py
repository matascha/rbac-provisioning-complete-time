#!/usr/bin/env python3
import os, json
from google.oauth2 import service_account
import google.auth.transport.requests
from datetime import datetime, timezone
import sys

if len(sys.argv) < 4:
    print("Usage: gen_gsuite_token.py <json_key_path> <impersonate_user> <cache_file>")
    sys.exit(1)

SERVICE_ACCOUNT_FILE = sys.argv[1]
ADMIN_EMAIL = sys.argv[2]
CACHE_FILE = sys.argv[3]
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]

# Check cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
        expiry = datetime.fromisoformat(cache["expires_at"])
        if expiry > datetime.now(timezone.utc):
            print(json.dumps(cache))
            sys.exit(0)

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
delegated = credentials.with_subject(ADMIN_EMAIL)
delegated.refresh(google.auth.transport.requests.Request())

token_data = {
    "access_token": delegated.token,
    "expires_at": delegated.expiry.isoformat()
}
