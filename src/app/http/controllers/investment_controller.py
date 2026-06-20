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
    def get_latest_investments() -> List[dict]:
        """
        Retrieves the most recent record for each asset from the database.
        """
        # Added current_price to the SELECT query
        query = """
            SELECT name, classification, code, extended_negotiation, 
                extended_negotiation_percentage, previous, current_price, variation_percentage
            FROM investments 
            WHERE id IN (
                SELECT MAX(id) 
                FROM investments 
                GROUP BY code
            )
        """
        rows = db.fetch_all(query)

        # Convert sqlite3.Row objects to standard Python dictionaries
        return [dict(row) for row in rows]

    @staticmethod
    def _save_to_db(data: dict) -> int:
        """
        Helper method to insert the investment data into the SQLite database.
        """
        # Added current_price to the INSERT query and values
        query = """
            INSERT INTO investments 
            (name, classification, code, extended_negotiation, extended_negotiation_percentage, previous, current_price, variation_percentage) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["name"],
            data["classification"],
            data["code"],
            data.get("extended_negotiation"),
            data.get("extended_negotiation_percentage"),
            data["previous"],
            data["current_price"],  # Getting the current price from the dictionary
            data["variation_percentage"],
        )

        return db.execute(query, params)
