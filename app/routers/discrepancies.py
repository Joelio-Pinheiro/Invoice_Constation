from fastapi import APIRouter, HTTPException
import pandas as pd
from services.data_service import DataService
from services.pdf_service import PDFGenerator
from services.drive_service import DriveService
from schemas.models import Discrepancy

router = APIRouter()
data_service = DataService()

@router.get("/discrepancies", response_model=list[Discrepancy])
async def get_all_discrepancies():
    try:
        return data_service.load_discrepancies()
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/discrepancies/process-planilhas")
async def process_planilhas():
    try:
        transportadoras = ["Loggi", "Logan"]
        data_service.clear_discrepancies()
        for transportadora in transportadoras:
            df_fatura, df_fretes, config = data_service.conexao(transportadora)
            df_discrepancias = data_service.verificar_discrepancias(df_fatura, df_fretes, config, transportadora)
            
            if not df_discrepancias.empty:
                discrepancies_list = df_discrepancias.to_dict('records')
                data_service.save_discrepancies(discrepancies_list)
                
        return {"message": "Planilhas processadas com sucesso"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.get("/discrepancies/{nf}/pdf")
async def generate_pdf(nf: str):
    try:
        data = data_service.load_discrepancies()
        discrepancy = next((item for item in data if item["NF"] == nf), None)
        if not discrepancy:
            raise HTTPException(404, detail="Discrepância não encontrada")
        
        drive = DriveService()
        pdf_buffer = PDFGenerator.generate_discrepancy_report(discrepancy)
        file = drive.upload_file(pdf_buffer, f"discrepancia_{nf}.pdf", "application/pdf")
        
        return {"pdf_url": file.get('webViewLink')}
    except Exception as e:
        raise HTTPException(500, detail=str(e))