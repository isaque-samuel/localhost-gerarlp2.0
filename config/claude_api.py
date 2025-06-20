import requests
import json
import time
from config.settings import Config

class ClaudeAPI:
    def __init__(self):
        self.api_key = Config.CLAUDE_API_KEY
        self.api_url = Config.CLAUDE_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
    
    def test_connection(self):
        """Testa conexão com a API do Claude"""
        if not self.api_key:
            return {
                'status': 'error',
                'message': 'API Key do Claude não configurada'
            }
        
        try:
            # Fazer uma requisição simples de teste
            result = self.send_message(
                "Você é um assistente útil.",
                "Responda apenas 'OK' para confirmar que está funcionando.",
                max_tokens=10
            )
            
            if result['success']:
                return {
                    'status': 'success',
                    'message': 'Conexão com Claude API funcionando!'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Erro na API: {result.get("error", "Desconhecido")}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro de conexão: {str(e)}'
            }
    
    def send_message(self, system_prompt, user_message, max_tokens=1000):
        """
        Envia mensagem para Claude API
        
        Args:
            system_prompt: Prompt do sistema
            user_message: Mensagem do usuário
            max_tokens: Máximo de tokens na resposta
            
        Returns:
            dict: Resultado da requisição
        """
        start_time = time.time()
        
        try:
            # Usar Claude 3.5 Sonnet - modelo mais recente e poderoso
            payload = {
                "model": "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet mais recente
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }
            
            print(f"🔄 Enviando requisição para Claude 3.5 Sonnet...")
            print(f"📊 Modelo: {payload['model']}")
            print(f"🎯 Max tokens: {max_tokens}")
            print(f"📝 System prompt length: {len(system_prompt)}")
            print(f"💬 User message length: {len(user_message)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120  # Aumentar timeout para 2 minutos
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            print(f"⏱️ Resposta recebida em {duration_ms}ms")
            print(f"📈 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso! Tokens usados: {data.get('usage', {})}")
                
                return {
                    'success': True,
                    'content': data['content'][0]['text'] if data.get('content') else '',
                    'usage': data.get('usage', {}),
                    'duration_ms': duration_ms
                }
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                print(f"❌ Erro na API: {error_msg}")
                print(f"📄 Response: {response.text[:500]}...")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'duration_ms': duration_ms,
                    'raw_response': response.text
                }
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout na requisição")
            return {
                'success': False,
                'error': 'Timeout na requisição (120s)',
                'duration_ms': int((time.time() - start_time) * 1000)
            }
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erro de conexão: {str(e)}")
            return {
                'success': False,
                'error': f'Erro de conexão: {str(e)}',
                'duration_ms': int((time.time() - start_time) * 1000)
            }
        except Exception as e:
            print(f"💥 Erro interno: {str(e)}")
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}',
                'duration_ms': int((time.time() - start_time) * 1000)
            }
    
    def estimate_tokens(self, text):
        """
        Estima número de tokens em um texto
        Claude 3.5: aproximadamente 1 token ≈ 3.5 caracteres
        """
        return int(len(text) / 3.5)

# Instância global
claude_client = ClaudeAPI()