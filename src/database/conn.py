import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        # Descobre a pasta atual (src/database) e define o caminho do banco
        self.db_dir = Path(__file__).resolve().parent
        self.db_path = self.db_dir / "database.db"

    def get_connection(self):
        """
        Cria e retorna uma conexão com o banco de dados.
        Configura o row_factory para retornar resultados como dicionários.
        """
        conn = sqlite3.connect(self.db_path)
        # O pulo do gato: permite acessar as colunas por nome (ex: linha['name'])
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self, migration_file="initial.sql"):
        """
        Lê o arquivo de migration e executa para criar as tabelas
        caso elas ainda não existam.
        """
        migration_path = self.db_dir / "migrations" / migration_file

        if not migration_path.exists():
            print(f"Aviso: Arquivo de migration {migration_path} não encontrado.")
            return

        with open(migration_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()

    def execute(self, query: str, params: tuple = ()):
        """
        Executa queries de INSERT, UPDATE ou DELETE.
        Retorna o ID da linha alterada/inserida.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def fetch_all(self, query: str, params: tuple = ()):
        """
        Executa queries de SELECT e retorna todas as linhas.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()


# Instância global (Singleton) para ser importada e usada no resto do app
db = DatabaseManager()
