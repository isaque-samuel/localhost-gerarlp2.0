import pymysql
import uuid
from datetime import datetime
from config.settings import Config

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Estabelece conexão com MySQL"""
        try:
            self.connection = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            print("✅ Conexão com MySQL estabelecida!")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar com MySQL: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Executa query e retorna resultados"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
        except Exception as e:
            print(f"❌ Erro ao executar query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
    
    def close(self):
        """Fecha conexão"""
        if self.connection:
            self.connection.close()
            print("🔌 Conexão com MySQL fechada")

# Instância global
db = Database()