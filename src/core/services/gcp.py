

import csv
import os
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from src.core.config.gcp import GCPConfig
from src.llm.env_config import get_config

load_dotenv(
    ".env"
)

env = get_config()
SCOPES = os.getenv("GCP_SCOPES").split(",")
SUBJECT = 'patrick@whatnow.is'

# # Initialize the Drive API
gcp_config = GCPConfig()

docs_service = gcp_config.get_google_service('docs', 'v1', SCOPES, SUBJECT)
spreadsheet_service = gcp_config.get_google_service('sheets', 'v4', SCOPES, SUBJECT)

def store_spreadsheet(spreadsheet_id: str):
    try:
        sheet_names = get_sheet_names(spreadsheet_id)

        print(f'Sheet names: {sheet_names}')
        
        for sheet_name in sheet_names:
            # Request the spreadsheet data
            result = spreadsheet_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()

            # Get the values from the response
            values = result.get('values', [])

            file_name = sheet_name.replace(' ', '_').lower()

            if file_name != "importances":
                data_dir = "tmp/csv/topics"
                if not os.path.isdir(data_dir):
                    os.makedirs(data_dir)
                # Write the values to a CSV file
                with open(f'{data_dir}/{file_name}.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(values)

    except HttpError as error:
        print(f'An error occurred: {error}')

def get_sheet_names(spreadsheet_id: str):
    try:
        # Request the spreadsheet metadata
        result = spreadsheet_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        # Get the sheet names from the response
        sheet_names = [sheet['properties']['title'] for sheet in result['sheets']]

        return sheet_names

    except HttpError as error:
        print(f'An error occurred: {error}')