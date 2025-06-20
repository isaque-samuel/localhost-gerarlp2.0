import uuid
import json
from datetime import datetime
from config.database import db

class GeneratedSkeleton:
    def __init__(self):
        self.skeleton_id = None
        self.request_id = None
        self.raw_skeleton_response_from_ai = None
        self.parsed_skeleton_data = None
        self.prompt_tokens_phase1 = 0
        self.completion_tokens_phase1 = 0
        self.duration_ms_phase1 = 0
        self.status = 'pending'
        self.error_details = None
        self.created_at = None
    
    def save(self):
        """Salva esqueleto no banco"""
        if not self.skeleton_id:
            self.skeleton_id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.now()
        
        query = """
        INSERT INTO generated_skeletons (
            skeleton_id, request_id, raw_skeleton_response_from_ai,
            parsed_skeleton_data, prompt_tokens_phase1, completion_tokens_phase1,
            duration_ms_phase1, status, error_details, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Converter parsed_skeleton_data para JSON se for dict
        parsed_data_json = None
        if self.parsed_skeleton_data:
            if isinstance(self.parsed_skeleton_data, dict):
                parsed_data_json = json.dumps(self.parsed_skeleton_data)
            else:
                parsed_data_json = self.parsed_skeleton_data
        
        params = (
            self.skeleton_id, self.request_id, self.raw_skeleton_response_from_ai,
            parsed_data_json, self.prompt_tokens_phase1, self.completion_tokens_phase1,
            self.duration_ms_phase1, self.status, self.error_details, self.created_at
        )
        
        result = db.execute_query(query, params)
        return result is not None
    
    def update_status(self, new_status, error_details=None):
        """Atualiza status do esqueleto"""
        query = """
        UPDATE generated_skeletons 
        SET status = %s, error_details = %s 
        WHERE skeleton_id = %s
        """
        
        params = (new_status, error_details, self.skeleton_id)
        return db.execute_query(query, params)
    
    @staticmethod
    def get_by_id(skeleton_id):
        """Busca esqueleto por ID"""
        query = "SELECT * FROM generated_skeletons WHERE skeleton_id = %s"
        result = db.execute_query(query, (skeleton_id,))
        
        if result and len(result) > 0:
            data = result[0]
            skeleton = GeneratedSkeleton()
            
            for key, value in data.items():
                if key == 'parsed_skeleton_data' and value:
                    try:
                        # Tentar parsear JSON
                        if isinstance(value, str):
                            setattr(skeleton, key, json.loads(value))
                        else:
                            setattr(skeleton, key, value)
                    except json.JSONDecodeError:
                        setattr(skeleton, key, None)
                else:
                    setattr(skeleton, key, value)
            
            return skeleton
        return None
    
    @staticmethod
    def get_by_request_id(request_id):
        """Busca esqueleto mais recente por request_id"""
        query = """
        SELECT * FROM generated_skeletons 
        WHERE request_id = %s AND status != 'replaced'
        ORDER BY created_at DESC 
        LIMIT 1
        """
        result = db.execute_query(query, (request_id,))
        
        if result and len(result) > 0:
            data = result[0]
            skeleton = GeneratedSkeleton()
            
            for key, value in data.items():
                if key == 'parsed_skeleton_data' and value:
                    try:
                        # Tentar parsear JSON
                        if isinstance(value, str):
                            setattr(skeleton, key, json.loads(value))
                        else:
                            setattr(skeleton, key, value)
                    except json.JSONDecodeError:
                        setattr(skeleton, key, None)
                else:
                    setattr(skeleton, key, value)
            
            return skeleton
        return None
    
    @staticmethod
    def get_all_by_request(request_id):
        """Lista todos os esqueletos de uma solicitação"""
        query = """
        SELECT skeleton_id, status, created_at, prompt_tokens_phase1, completion_tokens_phase1
        FROM generated_skeletons 
        WHERE request_id = %s 
        ORDER BY created_at DESC
        """
        return db.execute_query(query, (request_id,))