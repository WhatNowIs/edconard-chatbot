import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GCPConfig:
    def __init__(self):
        # Path to the GCP credentials file
        self.credentials_path = "config/gcp.json"
        self.credentials = None

    def get_gcp_credentials(self, scopes, subject):
        if self.credentials is None:
            # Load credentials from the JSON file
            try:
                with open(self.credentials_path, "r") as file:
                    credentials_data = json.load(file)
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_data, scopes=scopes
                ).with_subject(subject)
            except FileNotFoundError:
                raise RuntimeError(f"GCP credentials file not found at {self.credentials_path}")
            except json.JSONDecodeError:
                raise RuntimeError(f"Invalid JSON in GCP credentials file at {self.credentials_path}")
        return self.credentials

    def get_google_service(self, service_name, version, scopes, subject):
        # Ensure credentials are initialized
        self.get_gcp_credentials(scopes, subject)

        # Build the Google API client service
        return build(service_name, version, credentials=self.credentials)
