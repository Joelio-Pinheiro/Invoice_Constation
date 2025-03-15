from googleapiclient.discovery import build
from google.oauth2 import service_account
from config.settings import settings
import io
from googleapiclient.http import MediaIoBaseUpload

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
    
    def upload_file(self, file_data, file_name, mime_type):
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