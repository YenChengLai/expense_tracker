import json
import os
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SPREAD_SHEET_ID = os.environ.get("SPREAD_SHEET_ID")


def export(file_name: str, data: str) -> None:
    with open(file_name, mode="w", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=4, ensure_ascii=False))


def get_google_sheet_data(spreadsheet_id, prefix):
    """Fetches data from all sheets in a Google Sheet."""

    # Load credentials from environment variable
    creds = Credentials.from_service_account_info(
        json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    )
    service = build("sheets", "v4", credentials=creds)

    # Get all sheet titles
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get("sheets", [])

    # Create an empty dictionary to store all sheet data
    selected_data = []

    # Loop through all sheets and fetch data
    for sheet in sheets:
        sheet_title = sheet["properties"]["title"]
        if sheet_title.startswith(prefix):
            range_name = f"{sheet_title}!A1:E"
            try:
                response = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=spreadsheet_id, range=range_name)
                    .execute()
                )
                data = response.get("values", [])
                if data:
                    # Convert data to a Pandas DataFrame and then to a list of dictionaries
                    df = pd.DataFrame(data[1:], columns=data[0])
                    selected_data.extend(df.to_dict("records"))

            except Exception as e:
                print(f"An error occurred fetching data from {sheet_title}: {e}")

    return selected_data


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file

    month = datetime.now().month - 1
    month_string = f"{month:02d}"
    prefix = f"2024{month_string}"

    all_data = get_google_sheet_data(SPREAD_SHEET_ID, prefix)
    export(file_name="expense.json", data=all_data)
