import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageFile
import json
from config.settings import Config

# Permitir imagens truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True

class ImageProcessor:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_SIZE = (1920, 1080)  # Redimensionar imagens grandes
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename):
        """Verifica se extensão é permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_uploaded_file(self, file, prefix='img'):
        """Salva arquivo no servidor com nome único"""
        if not file or not self.is_allowed_file(file.filename):
            return None, "Tipo de arquivo não permitido"
        
        try:
            # Gerar nome único
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{prefix}_{uuid.uuid4().hex}.{extension}"
            
            # Caminho completo
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Salvar arquivo
            file.save(file_path)
            
            # Otimizar imagem
            self._optimize_image(file_path)
            
            # Retornar URL relativa
            relative_url = f"/static/uploads/{unique_filename}"
            
            return relative_url, None
        
        except Exception as e:
            return None, f"Erro ao processar arquivo: {str(e)}"
    
    def save_logo(self, file):
        """Salva logo da empresa"""
        return self.save_uploaded_file(file, prefix='logo')
    
    def save_multiple_images(self, files):
        """Salva múltiplas imagens"""
        results = {
            'success': [],
            'errors': []
        }
        
        for file in files:
            if file.filename:  # Verificar se arquivo foi selecionado
                url, error = self.save_uploaded_file(file, prefix='img')
                if url:
                    results['success'].append({
                        'original_name': file.filename,
                        'url': url
                    })
                else:
                    results['errors'].append({
                        'original_name': file.filename,
                        'error': error
                    })
        
        return results
    
    def _optimize_image(self, file_path):
        """Otimiza imagem (redimensiona se necessário)"""
        try:
            with Image.open(file_path) as img:
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Redimensionar se muito grande
                if img.size[0] > self.MAX_SIZE[0] or img.size[1] > self.MAX_SIZE[1]:
                    img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)
                
                # Salvar otimizada
                img.save(file_path, optimize=True, quality=85)
                
        except Exception as e:
            print(f"Erro ao otimizar imagem {file_path}: {e}")
    
    def get_image_info(self, file_path):
        """Obtém informações da imagem"""
        try:
            full_path = os.path.join(self.upload_folder, os.path.basename(file_path))
            
            with Image.open(full_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(full_path)
                }
        except Exception as e:
            return {'error': str(e)}