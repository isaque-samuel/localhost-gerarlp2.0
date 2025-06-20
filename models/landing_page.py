import uuid
from datetime import datetime
from config.database import db

class LandingPageRequest:
    def __init__(self):
        self.request_id = None
        self.client_id = None
        self.page_title = None
        self.page_slug = None
        self.company_name = None
        self.company_logo_url = None
        self.main_content_brief = None
        self.images_input = None
        self.sections_suggestion_input = None
        self.style_preferences_input = None
        self.js_requirements_input = None
        self.status = 'pending'
        self.final_html_content = None
        self.html_head = None
        self.html_footer = None
        self.final_custom_css = None
        self.final_javascript = None
        self.final_html_url = None
        self.error_message = None
        self.created_at = None
        self.updated_at = None
    
    def save(self):
        """Salva nova solicitação no banco"""
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()
        
        query = """
        INSERT INTO landing_page_requests (
            request_id, client_id, page_title, page_slug, company_name,
            company_logo_url, main_content_brief, images_input,
            sections_suggestion_input, style_preferences_input,
            js_requirements_input, status, final_html_content,
            html_head, html_footer, final_custom_css, final_javascript,
            final_html_url, error_message, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        params = (
            self.request_id, self.client_id, self.page_title, self.page_slug,
            self.company_name, self.company_logo_url, self.main_content_brief,
            self.images_input, self.sections_suggestion_input,
            self.style_preferences_input, self.js_requirements_input,
            self.status, self.final_html_content, self.html_head,
            self.html_footer, self.final_custom_css, self.final_javascript,
            self.final_html_url, self.error_message, self.created_at, self.updated_at
        )
        
        result = db.execute_query(query, params)
        return result is not None
    
    def update_status(self, new_status, error_message=None):
        """Atualiza status da solicitação"""
        query = """
        UPDATE landing_page_requests 
        SET status = %s, error_message = %s, updated_at = %s 
        WHERE request_id = %s
        """
        
        params = (new_status, error_message, datetime.now(), self.request_id)
        return db.execute_query(query, params)
    
    @staticmethod
    def get_by_id(request_id):
        """Busca solicitação por ID"""
        query = "SELECT * FROM landing_page_requests WHERE request_id = %s"
        result = db.execute_query(query, (request_id,))
        
        if result and len(result) > 0:
            data = result[0]
            request = LandingPageRequest()
            for key, value in data.items():
                setattr(request, key, value)
            return request
        return None
    
    @staticmethod
    def get_all(limit=20):
        """Lista todas as solicitações"""
        query = """
        SELECT request_id, page_title, company_name, status, created_at 
        FROM landing_page_requests 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        return db.execute_query(query, (limit,))