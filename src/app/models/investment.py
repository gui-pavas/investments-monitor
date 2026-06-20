from pydantic import BaseModel
from typing import List

# Model for the bulk sync request payload
class InvestmentSyncItem(BaseModel):
    code: str
    name: str

class BulkSyncRequest(BaseModel):
    items: List[InvestmentSyncItem]

# Assuming you already have this response model
class InvestmentResponse(BaseModel):
    name: str
    classification: str
    code: str
    extended_negotiation: float | None = None
    extended_negotiation_percentage: float | None = None
    previous: float
    current_price: float
    variation_percentage: float
    id_banco: int | None = None