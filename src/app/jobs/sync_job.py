import time
from apscheduler.schedulers.background import BackgroundScheduler
from src.app.http.controllers.investment_controller import InvestmentController
from src.app.models.investment import InvestmentSyncItem
from src.database.conn import db


def start_jobs():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_all, "interval", minutes=5)
    scheduler.start()

    fetch_and_store_all()


def fetch_and_store_all():
    print("⏳ [SCHEDULER] Coletando cotações em tempo real no Yahoo Finance...")
    try:
        rows = db.fetch_all("SELECT DISTINCT code, name FROM investments")
        if not rows:
            print(
                "⚠️ [SCHEDULER] Nenhum ativo encontrado na tabela 'investments' para atualizar."
            )
            return

        for row in rows:
            portfolio_item = [InvestmentSyncItem(code=row["code"], name=row["name"])]

            # Busca um por um e salva
            InvestmentController.sync_multiple_investments(portfolio_item)

            # 🔥 Pausa de 1 segundo para o Yahoo respirar e não dar Erro 502
            time.sleep(1.0)

        print("✅ [SCHEDULER] Banco de dados atualizado com as cotações reais!")
    except Exception as e:
        print(f"❌ [SCHEDULER] Erro durante a sincronização: {e}")
