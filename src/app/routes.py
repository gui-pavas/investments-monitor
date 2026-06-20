from fastapi import APIRouter
from typing import List
from src.app.http.controllers.investment_controller import InvestmentController
from src.app.models.investment import InvestmentResponse, BulkSyncRequest

router = APIRouter(prefix="/api")


@router.post("/sync/{code}", response_model=InvestmentResponse)
def sync_single_investment(code: str, name: str = "Desconhecido"):
    """
    Sincroniza um único ativo com o Yahoo Finance.
    """
    return InvestmentController.sync_single_investment(code, name)


@router.post("/sync", response_model=List[InvestmentResponse])
def sync_multiple_investments(payload: BulkSyncRequest):
    """
    Sincroniza uma lista de ativos com o Yahoo Finance de uma só vez.
    """
    return InvestmentController.sync_multiple_investments(payload.items)
