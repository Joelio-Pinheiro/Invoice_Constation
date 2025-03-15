## **Instalação**
### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/invoice-contestation-api.git
cd invoice-contestation-api
```

### **2. Configure o Ambiente Virtual**
#### **Linux/MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```
#### **Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
2. **Configure o arquivo de credenciais**:
   - No projeto, crie um arquivo chamado `credentials.json` na raiz.
   - Abra o arquivo e **copie o conteúdo do seu arquivo de credenciais** para ele.
   - Exemplo:
     ```json
     {
       "type": "service_account",
       "project_id": "seu-projeto-id",
       "private_key_id": "sua-private-key-id",
       "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
       "client_email": "seu-email-de-servico@seu-projeto.iam.gserviceaccount.com",
       "client_id": "seu-client-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/seu-email-de-servico%40seu-projeto.iam.gserviceaccount.com"
     }
     ```

### **3. Configure as Variáveis de Ambiente**
```bash
cp .env.example .env  # Linux/MacOS
copy .env.example .env  # Windows
```
Edite `.env` com os valores corretos:
```plaintext
DRIVE_FOLDER_ID=your_drive_folder_id
CREDENTIALS_FILE=credentials.json
```

### **4. Execute o Projeto**
```bash
cd app
uvicorn main:app --reload
```
API disponível em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## **Endpoints**
- `POST /api/v1/discrepancies/process-planilhas` → Processa planilhas de faturasn do Drive e salva.
- `GET /api/v1/discrepancies` → Lista todas as discrepâncias.
- `GET /api/v1/discrepancies/{nf}/pdf` → Gera um relatório em PDF e salva na pasta do drive configurada.
