import sqlite3
from src.database.conn import db

CLIENT_PORTFOLIO = [
    # --- Commodities & Futuros ---
    ("Petróleo Brent Futuros", "BZ=F"),
    ("Ouro Futuros", "GC=F"),
    ("Cobre Futuros", "HG=F"),
    ("Petróleo WTI Futuros", "CL=F"),
    ("Soja Chicago Futuros", "ZS=F"),
    ("Dow Jones Futuros", "YM=F"),
    ("Hang Seng Index", "^HSI"),
    ("FTSE China A50 Futuros", "XIN9.FGI"),
    ("S&P 500 VIX Futuros", "^VIX"),
    # --- Índices Globais ---
    ("Oslo OBX Index", "OBX.OL"),
    ("The Global Dow USD", "^GDOW"),
    ("BSE Sensex 30", "^BSESN"),
    ("Shanghai Composite", "000001.SS"),
    ("SZSE Component", "399001.SZ"),
    ("Índice Dólar Futuros", "DX-Y.NYB"),
    # --- Ações & ETFs ---
    ("Vale SA ADR", "VALE"),
    ("Petroleo Brasileiro Petrobras SA ADR", "PBR"),
    ("iShares MSCI Brazil ETF", "EWZ"),
    ("State Street® Financial Select Sector SPDR® ETF", "XLF"),
    ("State Street® Consumer Staples Select Sector SPDR® ETF", "XLP"),
    ("State Street® Energy Select Sector SPDR® ETF", "XLE"),
    ("State Street® SPDR® S&P® Metals & Mining ETF", "XME"),
    ("iShares MSCI Emerging Markets ETF", "EEM"),
    ("iShares Semiconductor ETF", "SOXX"),
    # --- Moedas / Câmbio (Padrão MOEDA=X) ---
    ("USD/MXN - Dólar Americano Peso Mexicano", "MXN=X"),
    ("USD/NOK - Dólar Americano Coroa Norueguesa", "NOK=X"),
    ("USD/NZD - Dólar Americano Dólar Neozelandês", "NZD=X"),
    ("USD/AUD - Dólar Americano Dólar Australiano", "AUD=X"),
    ("USD/KRW - Dólar Americano Won Sul-Coreano", "KRW=X"),
    ("USD/CNY - Dólar Americano Yuan Chinês", "CNY=X"),
    ("EUR/BRL - Euro Real Brasileiro", "EURBRL=X"),
    # --- Tesouro Americano (Renda Fixa EUA) ---
    ("EUA a 10 anos", "^TNX"),
    ("EUA a 5 anos", "^FVX"),
    ("EUA a 2 anos", "^IRX"),
]


def run_seeder():
    print("🛠️ [SEEDER] Garantindo que a tabela 'investments' existe...")
    try:
        db.setup_database("20260620010031_initial.sql")
    except Exception as e:
        print(f"⚠️ Nota ao estruturar banco: {e}")

    print("🌱 [SEEDER] Populando a tabela 'investments' com a carteira inicial...")

    # Inserindo direto na tabela principal de investimentos
    query = """
        INSERT INTO investments 
        (name, classification, code, extended_negotiation, extended_negotiation_percentage, previous, current_price, variation_percentage) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    count = 0
    for name, code in CLIENT_PORTFOLIO:
        try:
            # Criamos o registro "espelho" com dados zerados/nulos obrigatórios
            params = (
                name,
                "Aguardando Carga",  # classification
                code,
                None,  # extended_negotiation
                None,  # extended_negotiation_percentage
                0.0,  # previous
                0.0,  # current_price
                0.0,  # variation_percentage
            )
            db.execute(query, params)
            count += 1
        except Exception as e:
            print(f"⚠️ Erro ao inserir {name} ({code}): {e}")

    print(f"✅ [SEEDER] Sucesso! {count} ativos espelhados na tabela 'investments'.")


if __name__ == "__main__":
    run_seeder()
