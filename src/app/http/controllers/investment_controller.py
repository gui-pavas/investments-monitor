from typing import List
from fastapi import HTTPException
from src.app.services.investment_service import InvestmentService
from src.database.conn import db
from src.app.models.investment import InvestmentSyncItem


class InvestmentController:

    @staticmethod
    def sync_single_investment(code: str, name: str) -> dict:
        service = InvestmentService()
        data = service.fetch_data(code, name)

        if not data:
            # Texto para o usuário/cliente em PT-BR
            raise HTTPException(
                status_code=404,
                detail=f"Não foi possível encontrar dados para o código {code}",
            )

        # Save to database
        inserted_id = InvestmentController._save_to_db(data)
        data["id_banco"] = inserted_id

        return data

    @staticmethod
    def sync_multiple_investments(items: List[InvestmentSyncItem]) -> List[dict]:
        service = InvestmentService()
        results = []

        for item in items:
            data = service.fetch_data(item.code, item.name)

            if data:
                inserted_id = InvestmentController._save_to_db(data)
                data["id_banco"] = inserted_id
                results.append(data)

        return results

    @staticmethod
    def _save_to_db(data: dict) -> int:
        """
        Helper method to insert the investment data into the SQLite database.
        """
        query = """
            INSERT INTO investments 
            (name, classification, code, extended_negotiation, extended_negotiation_percentage, previous, variation_percentage) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["name"],
            data["classification"],
            data["code"],
            data.get("extended_negotiation"),
            data.get("extended_negotiation_percentage"),
            data["previous"],
            data["variation_percentage"],
        )

        return db.execute(query, params)
