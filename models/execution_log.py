import uuid
from datetime import datetime
from config.database import db

class ExecutionLog:
    def __init__(self, request_id, component, log_level, message, details=None):
        self.log_id = str(uuid.uuid4())
        self.request_id = request_id
        self.timestamp = datetime.now()
        self.component = component
        self.log_level = log_level  # INFO, WARNING, ERROR, DEBUG
        self.message = message
        self.details = details
    
    def save(self):
        """Salva log no banco"""
        query = """
        INSERT INTO execution_logs (
            log_id, request_id, timestamp, component, log_level, message, details
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            self.log_id, self.request_id, self.timestamp,
            self.component, self.log_level, self.message, self.details
        )
        
        return db.execute_query(query, params)
    
    @staticmethod
    def add_log(request_id, component, level, message, details=None):
        """Método estático para adicionar log rapidamente"""
        log = ExecutionLog(request_id, component, level, message, details)
        return log.save()
    
    @staticmethod
    def get_logs_by_request(request_id, limit=50):
        """Busca logs por request_id"""
        query = """
        SELECT * FROM execution_logs 
        WHERE request_id = %s 
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        return db.execute_query(query, (request_id, limit))