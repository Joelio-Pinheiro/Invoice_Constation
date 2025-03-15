import os
import json
import gspread
import pandas as pd
from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

from sqlalchemy import Numeric

from config import settings
from services.drive_service import SCOPES

class DataService:
    def __init__(self):
        self.creds = service_account.Credentials.from_service_account_file(
            "../" + settings.CREDENTIALS_FILE, scopes=SCOPES
        )
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    @staticmethod
    def clean_currency(value):
        if isinstance(value, (int, float)):
            return float(value)
        try:
            if value != '':
                value = str(value).strip()
                cleaned = ''.join(c for c in value if c.isdigit() or c in {',', '.'})
                if not cleaned:
                    raise ValueError(f"Valor inválido para conversão: '{value}'")
                return float(cleaned.replace(',', '.'))
        except Exception as e:
            print(f"Erro ao converter '{value}': {e}")
            return 0.0

    def conexao(self, transportadora: str):
        client = gspread.authorize(self.creds)

        config = {
            "Loggi": {
                "fatura": {
                    "sheet_name": "Cópia de  Fatura - Loggi",
                    "columns": {
                        "nfe": "Número NFe do Pacote/Produto",
                        "cep": "CEP Destino",
                        "peso": "Faixa de Peso",
                        "frete": "Valor Frete Peso",
                        "advalorem": "Advalorem",
                        "gris": "Gris",
                        "icms": "ICMS",
                        "aliquota_icms": "Alíquota ICMS",
                        "iss": "ISS",
                        "aliquota_iss": "Alíquota ISS"
                    },
                    "header_row": 0
                },
                "frete": {
                    "sheet_name": "Cópia de  542994_57539_70192_264 - Loggi - ES",
                    "header_row": 3,
                    "data_start": 4,
                    "cep_columns": ["CEPI", "CEPF"],
                    "faixas_peso": ['0.300', '0.500', '0.750', '1.000', '1.250', '1.500', 
                                   '2.000', '2.500', '3.000', '3.500', '4.000', '5.000',
                                   '6.000', '7.000', '8.000', '9.000', '10.000', '15.000',
                                   '20.000', '30.000'],
                    "tax_columns": ["FRETE VALOR SOBRE A NOTA(%)", "GRIS(%)", "SEGURO(%)"],
                    "excedente": "VALOR EXCEDENTE"
                }
            },
            "Logan": {
                "fatura": {
                    "sheet_name": "Cópia de Fatura - Logan",
                    "columns": {
                        "nfe": "Nota Fiscal",
                        "cep": "Cep",
                        "peso": "PesoTaxado",
                        "frete": "Frete",
                        "advalorem": "Advalorem",
                        "gris": "GRIS",
                        "icms": "ICMS",
                        "iss": "ISS",
                        "aliquota_iss": "Alíquota ISS",
                        "aliquota_icms": "ALIQUOTA DE ICMS",
                    },
                    "header_row": 0
                },
                "frete": {
                    "sheet_name": "Cópia de  514391_54253_70192_19145 - Logan - ES",
                    "header_row": 2,
                    "data_start": 3,
                    "cep_columns": ["CEPI", "CEPF"],
                    "faixas_peso": ['0.250', '0.500', '0.750', '1.000', '1.500',
                                   '2.000', '2.500', '3.000', '3.500', '4.000', '5.000',
                                   '6.000', '7.000', '8.000', '9.000', '10.000', '11.000', 
                                   '12.000', '13.000', '14.000', '15.000', '16.000',
                                   '17.000','18.000', '19.000','20.000', '21.000',
                                   '22.000', '23.000', '24.000', '25.000', '26.000',
                                   '27.000', '28.000', '29.000', '30.000'],	
                    "tax_columns": ["FRETE VALOR SOBRE A NOTA(%)", "GRIS(%)", "SEGURO(%)"],
                    "excedente": "VALOR EXCEDENTE"
                }
            }
        }

        # Carregar dados da fatura
        fatura_sheet = client.open(config[transportadora]["fatura"]["sheet_name"]).sheet1
        data_fatura = fatura_sheet.get_all_values()
        
        # Processar fatura
        fatura_config = config[transportadora]["fatura"]
        df_fatura = pd.DataFrame(data_fatura[fatura_config["header_row"]+1:], 
                               columns=data_fatura[fatura_config["header_row"]])
        
        df_fatura.columns = df_fatura.columns.str.strip()

        # Converter colunas numéricas
        for col in ['peso', 'frete', 'advalorem', 'gris', 'icms', 'iss', 'aliquota_icms', 'aliquota_iss']:
            col_name = fatura_config["columns"][col]
            if col_name in df_fatura.columns:
                df_fatura[col_name] = df_fatura[col_name].astype(str).apply(self.clean_currency)
            else:
                if col_name != 'ISS' or col_name != 'Alíquota ISS':
                    print(f"Aviso: Coluna {col_name} não encontrada na fatura.")

        # Carregar tabela de fretes
        frete_sheet = client.open(config[transportadora]["frete"]["sheet_name"]).sheet1
        data_frete = frete_sheet.get_all_values()

        # Processar fretes
        frete_config = config[transportadora]["frete"]
        headers = data_frete[3][2:]
        rows = data_frete[4:]
        rows_adjusted = [row[2:] for row in rows]
        df_fretes = pd.DataFrame(rows_adjusted, columns=headers)
        
        for col in frete_config["cep_columns"] + frete_config["faixas_peso"] + [frete_config["excedente"]] + frete_config["tax_columns"]:
            df_fretes[col] = df_fretes[col].apply(self.clean_currency)
        
        for col in frete_config["cep_columns"] + frete_config["faixas_peso"] + [frete_config["excedente"]] + frete_config.get("tax_columns", []):
            if col in df_fretes.columns:
                df_fretes[col] = df_fretes[col].apply(self.clean_currency)
            else:
                print(f"Aviso: Coluna {col} não encontrada na tabela de fretes.")
        
        return df_fatura, df_fretes, config[transportadora]
    
    def verificar_discrepancias(self, df_fatura, df_fretes, config, transportadora):
        def ensure_numeric(value):
            if isinstance(value, (int, float)):
                return float(value)
            return 0.0

        def is_empty(value):
            if value is None:
                return True
            if isinstance(value, str) and value.strip() == '':
                return True
            if isinstance(value, (int, float)) and pd.isna(value):
                return True
            return False

        discrepancias = []
        col = config["fatura"]["columns"]
        frete_cols = config["frete"]

        for _, row in df_fatura.iterrows():
            try:
                cep = int(row[col["cep"]].replace('-', ''))
                peso = float(row[col["peso"]])
                valor_cobrado = float(row[col["frete"]])
                
                df_fretes[frete_cols["cep_columns"]] = df_fretes[frete_cols["cep_columns"]].apply(pd.to_numeric, errors='coerce')
                frete_correto = df_fretes[
                    (df_fretes[frete_cols["cep_columns"][0]] <= cep) & 
                    (df_fretes[frete_cols["cep_columns"][1]] >= cep)
                ]

                if not frete_correto.empty:
                    valor_correto = None
                    for faixa in frete_cols["faixas_peso"]:
                        if peso <= float(faixa):
                            valor_correto = float(frete_correto.iloc[0][faixa])
                            break
                    else:
                        valor_correto = float(frete_correto.iloc[0][frete_cols["excedente"]])

                    if valor_correto is not None:
                        diferenca = valor_cobrado - valor_correto
                        if diferenca > 0.01:
                            taxa_frete_sobre_nota = float(frete_correto.iloc[0].get(frete_cols["tax_columns"][0], 0.0))
                            taxa_gris = float(frete_correto.iloc[0].get(frete_cols["tax_columns"][1], 0.0))
                            taxa_seguro = float(frete_correto.iloc[0].get(frete_cols["tax_columns"][2], 0.0))

                            imposto_advalorem_cobrado = float(row[col["advalorem"]]) if not is_empty(row[col["advalorem"]]) else 0.0
                            imposto_gris_cobrado = (valor_correto + imposto_advalorem_cobrado) * (taxa_gris / 100)

                            base_icms = valor_correto + imposto_advalorem_cobrado + imposto_gris_cobrado
                            imposto_icms_cobrado = base_icms * (float(row[col["aliquota_icms"]]) / 100) if not is_empty(row[col["aliquota_icms"]]) else 0.0

                            if col["iss"] in df_fatura.columns:
                                imposto_iss_cobrado = valor_correto * (float(row[col["aliquota_iss"]]) / 100) if not is_empty(row[col["aliquota_iss"]]) else 0.0
                            else:
                                imposto_iss_cobrado = 0.0

                            imposto_iss_cobrado = ensure_numeric(imposto_iss_cobrado)
                            imposto_icms_cobrado = ensure_numeric(imposto_icms_cobrado)

                            valor_total_correto = valor_correto + imposto_advalorem_cobrado + imposto_gris_cobrado + imposto_icms_cobrado + imposto_iss_cobrado

                            valor_total_cobrado = (
                                valor_cobrado + 
                                imposto_advalorem_cobrado + 
                                imposto_gris_cobrado + 
                                imposto_icms_cobrado + 
                                imposto_iss_cobrado
                            )

                            diferenca_total = valor_total_cobrado - valor_total_correto

                            discrepancias.append({
                                "Transportadora": transportadora,
                                "NF": row[col["nfe"]],
                                "CEP": f"{cep:08d}",
                                "Peso": round(peso, 3),
                                "Valor Cobrado (Frete)": round(valor_cobrado, 2),
                                "Valor Correto (Frete)": round(valor_correto, 2),
                                "Diferença (Frete)": round(diferenca, 2),
                                "Impostos Recalculados": {
                                    "Advalorem": round(imposto_advalorem_cobrado, 2),
                                    "GRIS": round(imposto_gris_cobrado, 2),
                                    "ICMS": round(imposto_icms_cobrado, 2),
                                    "ISS": round(imposto_iss_cobrado, 2)
                                },
                                "Valor Total Correto": round(valor_total_correto, 2),
                                "Valor Total Cobrado": round(valor_total_cobrado, 2),
                                "Diferença Total": round(diferenca_total, 2)
                            })
            except Exception as e:
                print(f"Erro ao processar linha {_}: {str(e)}")
        
        return pd.DataFrame(discrepancias)

    @staticmethod
    def save_discrepancies(new_data: List[Dict[str, Any]], filename: str = "discrepancies"):
        file_path = f"{filename}.json"
        
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    existing_data = json.load(file)
            except Exception as e:
                print(f"Erro ao carregar dados existentes: {str(e)}")
        
        combined_data = existing_data + new_data
        
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(combined_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            raise ValueError(f"Erro ao salvar o arquivo {file_path}: {str(e)}")

    def load_discrepancies(self, filename: str = "discrepancies") -> List[Dict[str, Any]]:
        file_path = f"{filename}.json"
        
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise ValueError(f"Erro ao carregar dados: {str(e)}")
    
    @staticmethod
    def clear_discrepancies(filename: str = "discrepancies"):
        """Limpa o arquivo JSON, deixando-o vazio."""
        file_path = f"{filename}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump([], file)
        except Exception as e:
            raise ValueError(f"Erro ao limpar o arquivo {file_path}: {str(e)}")