import json
import re
from datetime import datetime
from config.claude_api import claude_client
from models.skeleton import GeneratedSkeleton
from models.execution_log import ExecutionLog

class SkeletonGenerator:
    def __init__(self):
        self.claude = claude_client
    
    def generate_skeleton(self, request_obj, colors_data=None):
        """
        Gera esqueleto da landing page baseado no briefing
        
        Args:
            request_obj: Objeto LandingPageRequest
            colors_data: Dados das cores extraídas
            
        Returns:
            GeneratedSkeleton object
        """
        skeleton = GeneratedSkeleton()
        skeleton.request_id = request_obj.request_id
        
        try:
            # Log início
            ExecutionLog.add_log(
                request_obj.request_id,
                'SKELETON_GENERATOR',
                'INFO',
                'Iniciando geração de esqueleto'
            )
            
            # Preparar contexto
            system_prompt = self._build_system_prompt(request_obj, colors_data)
            user_message = self._build_user_message(request_obj)
            
            # Log do prompt
            ExecutionLog.add_log(
                request_obj.request_id,
                'SKELETON_GENERATOR',
                'INFO',
                'Enviando prompt para Claude API',
                json.dumps({
                    'system_prompt_length': len(system_prompt),
                    'user_message_length': len(user_message),
                    'estimated_tokens': self.claude.estimate_tokens(system_prompt + user_message)
                })
            )
            
            # Enviar para Claude
            result = self.claude.send_message(system_prompt, user_message, max_tokens=3000)
            
            # Salvar resposta bruta
            skeleton.raw_skeleton_response_from_ai = result.get('content', '')
            skeleton.duration_ms_phase1 = result.get('duration_ms', 0)
            
            if result.get('usage'):
                skeleton.prompt_tokens_phase1 = result['usage'].get('input_tokens', 0)
                skeleton.completion_tokens_phase1 = result['usage'].get('output_tokens', 0)
            
            if result['success']:
                # Tentar parsear JSON da resposta
                parsed_data = self._parse_skeleton_response(result['content'])
                
                if parsed_data:
                    skeleton.parsed_skeleton_data = parsed_data
                    skeleton.status = 'completed'
                    
                    ExecutionLog.add_log(
                        request_obj.request_id,
                        'SKELETON_GENERATOR',
                        'INFO',
                        'Esqueleto gerado com sucesso',
                        json.dumps({
                            'sections_count': len(parsed_data.get('sections', [])),
                            'tokens_used': skeleton.prompt_tokens_phase1 + skeleton.completion_tokens_phase1,
                            'duration_ms': skeleton.duration_ms_phase1
                        })
                    )
                else:
                    skeleton.status = 'parse_error'
                    skeleton.error_details = 'Não foi possível parsear resposta JSON'
                    
                    ExecutionLog.add_log(
                        request_obj.request_id,
                        'SKELETON_GENERATOR',
                        'ERROR',
                        'Erro ao parsear resposta do Claude',
                        result['content'][:500] + '...' if len(result['content']) > 500 else result['content']
                    )
            else:
                skeleton.status = 'api_error'
                skeleton.error_details = result.get('error', 'Erro desconhecido na API')
                
                ExecutionLog.add_log(
                    request_obj.request_id,
                    'SKELETON_GENERATOR',
                    'ERROR',
                    'Erro na API do Claude',
                    skeleton.error_details
                )
            
            # Salvar no banco
            skeleton.save()
            
            return skeleton
            
        except Exception as e:
            skeleton.status = 'system_error'
            skeleton.error_details = str(e)
            
            ExecutionLog.add_log(
                request_obj.request_id,
                'SKELETON_GENERATOR',
                'ERROR',
                'Erro interno no gerador de esqueleto',
                str(e)
            )
            
            skeleton.save()
            return skeleton
    
    def _build_system_prompt(self, request_obj, colors_data):
        """Constrói prompt do sistema com contexto completo"""
        
        # Processar cores
        colors_info = "Cores não definidas"
        primary_color = "#2563eb"
        secondary_color = "#64748b"
        accent_color = "#f59e0b"
        
        if colors_data and isinstance(colors_data, dict):
            primary_color = colors_data.get('primary', '#2563eb')
            secondary_color = colors_data.get('secondary', '#64748b')
            accent_color = colors_data.get('accent', '#f59e0b')
            
            colors_info = f"""
            - Cor Primária (60%): {primary_color}
            - Cor Secundária (30%): {secondary_color}
            - Cor de Destaque (10%): {accent_color}
            """
        
        # Processar imagens
        images_info = "Nenhuma imagem fornecida"
        if request_obj.images_input:
            try:
                images = json.loads(request_obj.images_input)
                images_info = f"{len(images)} imagens fornecidas pelo cliente"
            except:
                pass
        
        system_prompt = f"""
Você é um especialista em UX/UI Design e desenvolvimento web, especializado em criar landing pages de alta conversão.

CONTEXTO DO PROJETO:
- Empresa: {request_obj.company_name or 'Não informado'}
- Título da Página: {request_obj.page_title}
- Logo: {'Fornecida' if request_obj.company_logo_url else 'Não fornecida'}
- {images_info}

PALETA DE CORES EXTRAÍDA:
{colors_info}

SUA TAREFA:
Analisar o briefing do cliente e criar um esqueleto estruturado da landing page seguindo as melhores práticas de conversão e UX.

DIRETRIZES OBRIGATÓRIAS:
1. Usar APENAS as cores fornecidas na paleta
2. Seguir a regra 60-30-10 (primária 60%, secundária 30%, destaque 10%)
3. Criar entre 4-7 seções principais
4. Focar em conversão e experiência do usuário
5. Considerar responsividade mobile-first

ESTRUTURA DE RESPOSTA OBRIGATÓRIA (JSON):
{{
  "sections": [
    {{
      "name": "hero",
      "order": 1,
      "title": "Título da Seção",
      "description": "Descrição do que a seção faz",
      "elements": ["elemento1", "elemento2"],
      "style_notes": "Notas específicas de estilo",
      "content_guidelines": "Diretrizes de conteúdo"
    }}
  ],
  "visual_identity": {{
    "primary_color": "{primary_color}",
    "secondary_color": "{secondary_color}",
    "accent_color": "{accent_color}",
    "font_primary": "Nome da fonte principal",
    "font_secondary": "Nome da fonte secundária",
    "layout_style": "modern_grid|classic|minimal",
    "spacing_unit": "1.5rem"
  }},
  "global_context": {{
    "business_type": "Tipo de negócio identificado",
    "tone_of_voice": "Tom de voz apropriado",
    "target_audience": "Público-alvo identificado",
    "primary_goal": "Objetivo principal da página",
    "secondary_goals": ["objetivo1", "objetivo2"]
  }},
  "conversion_strategy": {{
    "primary_cta": "Texto do CTA principal",
    "secondary_cta": "Texto do CTA secundário",
    "value_proposition": "Proposta de valor principal",
    "trust_elements": ["elemento1", "elemento2"],
    "urgency_elements": ["elemento1", "elemento2"]
  }}
}}

SEÇÕES RECOMENDADAS (escolha as mais adequadas):
- hero: Seção principal com título, subtítulo e CTA
- about: Sobre a empresa/produto
- services: Serviços ou produtos oferecidos
- benefits: Benefícios e diferenciais
- testimonials: Depoimentos de clientes
- pricing: Preços e planos
- contact: Contato e formulário
- faq: Perguntas frequentes

RESPONDA APENAS COM O JSON VÁLIDO, SEM TEXTO ADICIONAL.
"""
        return system_prompt
    
    def _build_user_message(self, request_obj):
        """Constrói mensagem do usuário com o briefing"""
        return f"""
Analise este briefing e crie o esqueleto da landing page:

BRIEFING DO CLIENTE:
{request_obj.main_content_brief}

Gere o esqueleto em JSON seguindo exatamente a estrutura especificada no system prompt.
"""
    
    def _parse_skeleton_response(self, response_content):
        """Tenta parsear a resposta JSON do Claude"""
        try:
            # Limpar resposta (remover markdown se houver)
            cleaned_content = response_content.strip()
            
            # Remover blocos de código markdown se existirem
            if cleaned_content.startswith('```'):
                lines = cleaned_content.split('\n')
                # Remover primeira linha (```json ou ```)
                lines = lines[1:]
                # Remover última linha se for ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned_content = '\n'.join(lines)
            
            # Tentar parsear JSON
            parsed_data = json.loads(cleaned_content)
            
            # Validar estrutura básica
            if self._validate_skeleton_structure(parsed_data):
                return parsed_data
            else:
                return None
                
        except json.JSONDecodeError as e:
            # Tentar extrair JSON usando regex como fallback
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group())
                    if self._validate_skeleton_structure(parsed_data):
                        return parsed_data
                except:
                    pass
            return None
        except Exception:
            return None
    
    def _validate_skeleton_structure(self, data):
        """Valida se a estrutura do esqueleto está correta"""
        try:
            # Verificar chaves obrigatórias
            required_keys = ['sections', 'visual_identity', 'global_context']
            if not all(key in data for key in required_keys):
                return False
            
            # Verificar se sections é uma lista não vazia
            sections = data.get('sections', [])
            if not isinstance(sections, list) or len(sections) == 0:
                return False
            
            # Verificar estrutura de cada seção
            for section in sections:
                required_section_keys = ['name', 'order', 'title', 'description']
                if not all(key in section for key in required_section_keys):
                    return False
            
            # Verificar visual_identity
            visual_identity = data.get('visual_identity', {})
            required_visual_keys = ['primary_color', 'secondary_color', 'accent_color']
            if not all(key in visual_identity for key in required_visual_keys):
                return False
            
            return True
            
        except Exception:
            return False
    
    def regenerate_skeleton(self, skeleton_id):
        """Regenera um esqueleto existente"""
        try:
            skeleton = GeneratedSkeleton.get_by_id(skeleton_id)
            if not skeleton:
                return None
            
            # Buscar request original
            from models.landing_page import LandingPageRequest
            request_obj = LandingPageRequest.get_by_id(skeleton.request_id)
            if not request_obj:
                return None
            
            # Buscar cores
            colors_data = None
            if request_obj.style_preferences_input:
                try:
                    style_prefs = json.loads(request_obj.style_preferences_input)
                    colors_data = style_prefs.get('brand_colors', {})
                except:
                    pass
            
            # Gerar novo esqueleto
            new_skeleton = self.generate_skeleton(request_obj, colors_data)
            
            # Marcar o antigo como substituído
            if new_skeleton and new_skeleton.status == 'completed':
                skeleton.update_status('replaced', f'Substituído por {new_skeleton.skeleton_id}')
            
            return new_skeleton
            
        except Exception as e:
            ExecutionLog.add_log(
                skeleton.request_id if skeleton else 'unknown',
                'SKELETON_GENERATOR',
                'ERROR',
                'Erro ao regenerar esqueleto',
                str(e)
            )
            return None
