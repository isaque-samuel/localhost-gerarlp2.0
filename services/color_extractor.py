import os
from PIL import Image
from collections import Counter
import colorsys
from config.settings import Config

class ColorExtractor:
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
    
    def extract_colors_from_logo(self, logo_url):
        """Extrai 3 cores seguindo regra 60-30-10 do design"""
        try:
            # Converter URL relativa para caminho absoluto
            filename = os.path.basename(logo_url)
            file_path = os.path.join(self.upload_folder, filename)
            
            if not os.path.exists(file_path):
                return self._get_fallback_colors(), "Arquivo de logo não encontrado"
            
            # Abrir e processar imagem
            with Image.open(file_path) as img:
                # Converter para RGB
                img = img.convert('RGB')
                
                # Redimensionar para acelerar processamento
                img.thumbnail((150, 150))
                
                # Obter cores dominantes
                colors = self._extract_design_palette(img)
                
                return colors, None
                
        except Exception as e:
            return self._get_fallback_colors(), f"Erro ao processar logo: {str(e)}"
    
    def _extract_design_palette(self, img):
        """Extrai paleta seguindo regra 60-30-10"""
        # Obter todos os pixels
        pixels = list(img.getdata())
        
        # Filtrar pixels muito claros ou muito escuros
        filtered_pixels = []
        for r, g, b in pixels:
            brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
            if 0.1 < brightness < 0.9:  # Ignorar muito claro/escuro
                filtered_pixels.append((r, g, b))
        
        if not filtered_pixels:
            filtered_pixels = pixels  # Usar todos se filtro removeu tudo
        
        # Contar cores mais frequentes
        color_counts = Counter(filtered_pixels)
        common_colors = color_counts.most_common(10)
        
        if len(common_colors) == 0:
            return self._get_fallback_colors()
        
        # Cor dominante (60%) - mais frequente
        primary_color = common_colors[0][0]
        
        # Se temos pelo menos 2 cores distintas
        if len(common_colors) >= 2:
            secondary_color = self._find_complementary_color(primary_color, [c[0] for c in common_colors[1:]])
        else:
            secondary_color = self._generate_complementary_color(primary_color)
        
        # Cor de destaque (10%) - contraste com as outras
        accent_color = self._generate_accent_color(primary_color, secondary_color)
        
        # Converter para hex
        palette = {
            'primary': self._rgb_to_hex(*primary_color),      # 60%
            'secondary': self._rgb_to_hex(*secondary_color),  # 30%
            'accent': self._rgb_to_hex(*accent_color)         # 10%
        }
        
        return palette
    
    def _find_complementary_color(self, primary_color, available_colors):
        """Encontra cor complementar entre as disponíveis"""
        best_color = available_colors[0]
        best_distance = 0
        
        for color in available_colors[:5]:  # Testar apenas as 5 mais comuns
            distance = self._color_distance(primary_color, color)
            if distance > best_distance and distance > 50:  # Mínimo de contraste
                best_distance = distance
                best_color = color
        
        return best_color
    
    def _generate_complementary_color(self, primary_color):
        """Gera cor complementar baseada na primária"""
        r, g, b = primary_color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Cor complementar (oposta no círculo cromático)
        comp_h = (h + 0.5) % 1.0
        comp_s = max(0.3, s * 0.8)  # Reduzir saturação
        comp_v = min(0.9, v * 1.1)  # Ajustar brilho
        
        comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, comp_s, comp_v)
        return (int(comp_r * 255), int(comp_g * 255), int(comp_b * 255))
    
    def _generate_accent_color(self, primary_color, secondary_color):
        """Gera cor de destaque que contrasta com as outras duas"""
        r1, g1, b1 = primary_color
        r2, g2, b2 = secondary_color
        
        # Converter para HSV
        h1, s1, v1 = colorsys.rgb_to_hsv(r1/255, g1/255, b1/255)
        h2, s2, v2 = colorsys.rgb_to_hsv(r2/255, g2/255, b2/255)
        
        # Criar cor de destaque
        accent_h = (h1 + 0.33) % 1.0  # Triádica
        accent_s = min(1.0, max(s1, s2) * 1.2)  # Alta saturação
        accent_v = 0.8 if (v1 + v2) / 2 > 0.5 else 0.9  # Contraste de brilho
        
        accent_r, accent_g, accent_b = colorsys.hsv_to_rgb(accent_h, accent_s, accent_v)
        return (int(accent_r * 255), int(accent_g * 255), int(accent_b * 255))
    
    def _color_distance(self, color1, color2):
        """Calcula distância entre duas cores RGB"""
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return ((r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2) ** 0.5
    
    def _rgb_to_hex(self, r, g, b):
        """Converte RGB para hex"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _get_fallback_colors(self):
        """Cores padrão seguindo regra 60-30-10"""
        return {
            'primary': "#2563eb",    # Azul (60%)
            'secondary': "#64748b",  # Cinza azulado (30%)
            'accent': "#f59e0b"      # Laranja (10%)
        }
    
    def validate_color_palette(self, colors):
        """Valida se as cores formam uma boa paleta"""
        if not isinstance(colors, dict) or len(colors) != 3:
            return False
        
        required_keys = ['primary', 'secondary', 'accent']
        if not all(key in colors for key in required_keys):
            return False
        
        # Validar formato hex
        import re
        hex_pattern = r'^#[0-9A-Fa-f]{6}$'
        return all(re.match(hex_pattern, colors[key]) for key in required_keys)