# test_db.py
from src.database.conn import db

# 1. Cria a tabela rodando a migration
# (Troque o nome do arquivo se a sua migration tiver ficado com a data na frente)
db.setup_database("20260620010031_initial.sql")

# 2. Insere um dado falso
novo_id = db.execute(
    """
    INSERT INTO investments (name, classification, code, previous, variation_percentage) 
    VALUES (?, ?, ?, ?, ?)
""",
    ("Petróleo Brent Futuros", "Queda", "LCO", 79.85, 0.0066),
)

print(f"Salvo com sucesso! ID: {novo_id}")

# 3. Puxa do banco
ativos = db.fetch_all("SELECT * FROM investments")
for ativo in ativos:
    print(
        f"O ativo {ativo['name']} (Código: {ativo['code']}) foi salvo às {ativo['timestamp']}"
    )
