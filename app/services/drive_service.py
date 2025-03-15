from googleapiclient.discovery import build
from google.oauth2 import service_account
from config.settings import settings
import io
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class DriveService:
    def __init__(self):
        self.creds = service_account.Credentials.from_service_account_file(
            "../" + settings.CREDENTIALS_FILE, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def _find_existing_files(self, file_name):
        query = f"name='{file_name}' and '{settings.DRIVE_FOLDER_ID}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            fields="files(id)"
        ).execute()
        return results.get('files', [])

    def upload_file(self, file_data, file_name, mime_type):
        try:
            existing_files = self._find_existing_files(file_name)
            for file in existing_files:
                self.service.files().delete(fileId=file['id']).execute()

            file_metadata = {
                'name': file_name,
                'parents': [settings.DRIVE_FOLDER_ID]
            }

            if isinstance(file_data, io.BytesIO):
                file_data.seek(0)
                media_body = MediaIoBaseUpload(file_data, mimetype=mime_type, resumable=True)
            else:
                raise ValueError("file_data deve ser uma instância de io.BytesIO")

            file = self.service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id,webViewLink'
            ).execute()

            return file

        except HttpError as error:
            print(f'Ocorreu um erro no Google Drive: {error}')
            raise