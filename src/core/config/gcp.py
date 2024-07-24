import os
import boto3
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.llm.env_config import get_config

class GCPConfig:
    def __init__(self, bucket_name, credentials_file_key):
        self.env = get_config()
        self.bucket_name = bucket_name
        self.credentials_file_key = credentials_file_key
        self.s3_client = boto3.client(
            's3', 
            aws_access_key_id=self.env.aws_key,
            aws_secret_access_key=self.env.aws_secret,
            region_name=self.env.s3_region
        )
        self.credentials = None

    def fetch_credentials(self):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.credentials_file_key)
            self.credentials = response['Body'].read().decode('utf-8')
        except Exception as e:
            # Log and handle the exception
            raise e


    def get_gcp_credentials(self, scopes, subject):
        if self.credentials is None:
            self.fetch_credentials()
            
        # Load credentials from string
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(self.credentials), scopes=scopes)
        
        return credentials.with_subject(subject)

    def get_google_service(self, service_name, version, scopes, subject):
        if self.credentials is None:
            self.credentials = self.get_gcp_credentials(scopes, subject)

        return build(service_name, version, credentials=self.credentials)
