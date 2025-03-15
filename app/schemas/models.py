from typing import Dict
from pydantic import BaseModel

from pydantic import BaseModel, Field

class Discrepancy(BaseModel):
    Transportadora: str
    NF: str = Field(alias="NF")
    CEP: str = Field(alias="CEP")
    Peso: float = Field(alias="Peso")
    Valor_Cobrado: float = Field(alias="Valor Cobrado (Frete)")
    Valor_Correto: float = Field(alias="Valor Correto (Frete)")
    Diferenca: float = Field(alias="Diferença (Frete)")
    Impostos_Recalculados: Dict[str, float] = Field(alias="Impostos Recalculados", default=None)
    Valor_Total_Correto: float = Field(alias="Valor Total Correto", default=None)
    Valor_Total_Cobrado: float = Field(alias="Valor Total Cobrado", default=None)
    Diferenca_Total: float = Field(alias="Diferença Total", default=None)      
    