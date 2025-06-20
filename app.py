import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json

from config.settings import Config
from config.database import db
from models.landing_page import LandingPageRequest
from models.execution_log import ExecutionLog
from services.image_processor import ImageProcessor
from services.color_extractor import ColorExtractor
from config.claude_api import claude_client
from services.skeleton_generator import SkeletonGenerator
from models.skeleton import GeneratedSkeleton

# Criar diretórios necessários
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/generated', exist_ok=True)

app = Flask(__name__)
app.config.from_object(Config)

# Instanciar serviços
image_processor = ImageProcessor()
color_extractor = ColorExtractor()
skeleton_generator = SkeletonGenerator()

def create_page_slug(page_title):
    """Cria slug único para a página"""
    import re
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', page_title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    # Adicionar timestamp para evitar duplicatas
    from time import time
    return f"{slug}-{int(time())}"

@app.route('/')
def index():
    """Página inicial"""
    try:
        # Buscar solicitações recentes
        requests = LandingPageRequest.get_all(limit=10)
        
        # Verificar status do Claude
        claude_status = 'not_configured'
        if Config.CLAUDE_API_KEY:
            try:
                test_result = claude_client.test_connection()
                claude_status = 'connected' if test_result['status'] == 'success' else 'error'
            except:
                claude_status = 'error'
        
        return render_template('index.html', 
                             requests=requests or [], 
                             claude_status=claude_status)
    except Exception as e:
        flash(f'Erro ao carregar dados: {str(e)}', 'error')
        return render_template('index.html', requests=[], claude_status='error')

@app.route('/create-request', methods=['POST'])
def create_request():
    """Nova rota para criar solicitação com upload de arquivos"""
    try:
        # Criar nova solicitação
        request_obj = LandingPageRequest()
        request_obj.page_title = request.form.get('page_title')
        request_obj.company_name = request.form.get('company_name')
        request_obj.main_content_brief = request.form.get('main_content_brief')
        request_obj.page_slug = create_page_slug(request_obj.page_title)
        request_obj.status = 'processing_uploads'
        
        upload_results = {
            'logo': None,
            'images': [],
            'colors': {},
            'errors': []
        }
        
        # Processar upload de logo
        logo_file = request.files.get('company_logo')
        if logo_file and logo_file.filename:
            ExecutionLog.add_log(
                request_obj.request_id or 'temp', 
                'UPLOAD', 
                'INFO', 
                f'Processando logo: {logo_file.filename}'
            )
            
            logo_url, logo_error = image_processor.save_logo(logo_file)
            if logo_url:
                request_obj.company_logo_url = logo_url
                upload_results['logo'] = logo_url
                
                # Extrair cores da logo (formato estruturado)
                colors, color_error = color_extractor.extract_colors_from_logo_structured(logo_url)
                if colors:
                    upload_results['colors'] = colors
                    request_obj.style_preferences_input = json.dumps({
                        'brand_colors': colors,
                        'color_extraction_method': '60-30-10_rule',
                        'extracted_from_logo': True,
                        'user_edited': False
                    })
                    
                    ExecutionLog.add_log(
                        request_obj.request_id or 'temp', 
                        'COLOR_EXTRACTOR', 
                        'INFO', 
                        'Cores extraídas com sucesso',
                        json.dumps({
                            'primary': colors['primary'],
                            'secondary': colors['secondary'], 
                            'accent': colors['accent'],
                            'method': '60-30-10 design rule'
                        })
                    )
                else:
                    upload_results['errors'].append(f'Erro ao extrair cores: {color_error}')
            else:
                upload_results['errors'].append(f'Erro no upload do logo: {logo_error}')
        
        # Processar upload de imagens múltiplas
        image_files = request.files.getlist('site_images')
        if image_files and any(f.filename for f in image_files):
            ExecutionLog.add_log(
                request_obj.request_id or 'temp', 
                'UPLOAD', 
                'INFO', 
                f'Processando {len(image_files)} imagens'
            )
            
            images_result = image_processor.save_multiple_images(image_files)
            upload_results['images'] = images_result['success']
            upload_results['errors'].extend([f"Imagem {err['original_name']}: {err['error']}" for err in images_result['errors']])
            
            # Salvar URLs das imagens no banco
            if images_result['success']:
                image_urls = [img['url'] for img in images_result['success']]
                request_obj.images_input = json.dumps(image_urls)
        
        # Definir status final baseado nos resultados
        if upload_results['errors']:
            request_obj.status = 'upload_errors'
            request_obj.error_message = '; '.join(upload_results['errors'])
        else:
            request_obj.status = 'uploads_completed'
        
        # Salvar no banco
        if request_obj.save():
            # Log de sucesso
            ExecutionLog.add_log(
                request_obj.request_id, 
                'SYSTEM', 
                'INFO', 
                'Solicitação criada com uploads processados',
                json.dumps({
                    'logo_uploaded': bool(upload_results['logo']),
                    'images_uploaded': len(upload_results['images']),
                    'colors_extracted': bool(upload_results['colors']),
                    'errors_count': len(upload_results['errors'])
                })
            )
            
            # Mensagem de sucesso
            success_msg = f"✅ Solicitação criada!"
            if upload_results['colors']:
                success_msg += f" Paleta de cores extraída (60-30-10)."
            if upload_results['images']:
                success_msg += f" {len(upload_results['images'])} imagens carregadas."
            
            flash(success_msg, 'success')
            
            # Alertas para erros não críticos
            if upload_results['errors']:
                for error in upload_results['errors']:
                    flash(f"⚠️ {error}", 'warning')
            
            return redirect(url_for('view_request', request_id=request_obj.request_id))
        else:
            flash('❌ Erro ao salvar solicitação no banco', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'❌ Erro ao processar solicitação: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/update-colors/<request_id>', methods=['POST'])
def update_colors(request_id):
    """Atualizar cores da paleta"""
    try:
        request_obj = LandingPageRequest.get_by_id(request_id)
        if not request_obj:
            return jsonify({'error': 'Solicitação não encontrada'}), 404
        
        # Receber novas cores
        new_colors = {
            'primary': request.form.get('primary_color'),
            'secondary': request.form.get('secondary_color'),
            'accent': request.form.get('accent_color')
        }
        
        # Validar cores
        if not color_extractor.validate_color_palette(new_colors):
            return jsonify({'error': 'Cores inválidas'}), 400
        
        # Atualizar no banco
        current_prefs = {}
        if request_obj.style_preferences_input:
            try:
                current_prefs = json.loads(request_obj.style_preferences_input)
            except:
                pass
        
        current_prefs.update({
            'brand_colors': new_colors,
            'user_edited': True,
            'last_edited': datetime.now().isoformat()
        })
        
        # Salvar
        query = "UPDATE landing_page_requests SET style_preferences_input = %s, updated_at = %s WHERE request_id = %s"
        result = db.execute_query(query, (json.dumps(current_prefs), datetime.now(), request_id))
        
        if result:
            # Log da alteração
            ExecutionLog.add_log(
                request_id, 
                'USER_EDIT', 
                'INFO', 
                'Paleta de cores editada pelo usuário',
                json.dumps(new_colors)
            )
            
            return jsonify({
                'success': True,
                'message': 'Cores atualizadas com sucesso!',
                'colors': new_colors
            })
        else:
            return jsonify({'error': 'Erro ao salvar no banco'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-create', methods=['POST'])
def test_create():
    """Rota de teste para criar solicitação simples (sem uploads)"""
    try:
        # Criar nova solicitação
        request_obj = LandingPageRequest()
        request_obj.page_title = request.form.get('page_title')
        request_obj.company_name = request.form.get('company_name')
        request_obj.main_content_brief = request.form.get('main_content_brief')
        request_obj.page_slug = create_page_slug(request_obj.page_title)
        request_obj.status = 'pending'
        
        # Salvar no banco
        if request_obj.save():
            # Adicionar log de sucesso
            ExecutionLog.add_log(
                request_obj.request_id, 
                'SYSTEM', 
                'INFO', 
                'Solicitação criada com sucesso (modo teste)',
                json.dumps({
                    'page_title': request_obj.page_title,
                    'company_name': request_obj.company_name,
                    'slug': request_obj.page_slug
                })
            )
            
            flash('✅ Solicitação criada com sucesso! (Modo teste)', 'success')
            return redirect(url_for('view_request', request_id=request_obj.request_id))
        else:
            flash('❌ Erro ao salvar solicitação no banco', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'❌ Erro ao criar solicitação: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/request/<request_id>')
def view_request(request_id):
    """Visualizar solicitação específica"""
    try:
        request_obj = LandingPageRequest.get_by_id(request_id)
        if not request_obj:
            flash('Solicitação não encontrada', 'error')
            return redirect(url_for('index'))
        
        # Buscar logs relacionados
        logs = ExecutionLog.get_logs_by_request(request_id, limit=20)
        
        # Buscar skeleton se existir
        skeleton = None
        if request_obj.status == 'skeleton_completed':
            skeleton = GeneratedSkeleton.get_by_request_id(request_id)
        
        # Buscar informações de upload (placeholder - será implementado na Fase 1)
        upload_info = {
            'logo': request_obj.company_logo_url,
            'images': [],
            'colors': []
        }
        
        # Se houver style_preferences_input, extrair cores
        if request_obj.style_preferences_input:
            try:
                style_prefs = json.loads(request_obj.style_preferences_input)
                brand_colors = style_prefs.get('brand_colors', {})
                if brand_colors:
                    upload_info['colors'] = [
                        brand_colors.get('primary', ''),
                        brand_colors.get('secondary', ''),
                        brand_colors.get('accent', '')
                    ]
                    upload_info['colors'] = [c for c in upload_info['colors'] if c]
            except:
                pass
        
        # Se houver images_input, extrair URLs
        if request_obj.images_input:
            try:
                images = json.loads(request_obj.images_input)
                upload_info['images'] = images if isinstance(images, list) else []
            except:
                pass
        
        return render_template('view_request.html', 
                             request=request_obj, 
                             logs=logs or [],
                             skeleton=skeleton,
                             upload_info=upload_info)
    except Exception as e:
        flash(f'Erro ao carregar solicitação: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/regenerate-skeleton-by-request/<request_id>', methods=['POST'])
def regenerate_skeleton_by_request(request_id):
    """Regenerar esqueleto por request_id"""
    try:
        # Buscar skeleton existente
        skeleton = GeneratedSkeleton.get_by_request_id(request_id)
        if not skeleton:
            return jsonify({
                'success': False,
                'error': 'Nenhum esqueleto encontrado para regenerar'
            })
        
        # Regenerar usando o skeleton_id
        new_skeleton = skeleton_generator.regenerate_skeleton(skeleton.skeleton_id)
        
        if new_skeleton and new_skeleton.status == 'completed':
            return jsonify({
                'success': True,
                'message': 'Esqueleto regenerado com sucesso!',
                'skeleton_id': new_skeleton.skeleton_id,
                'redirect_url': url_for('view_skeleton', skeleton_id=new_skeleton.skeleton_id)
            })
        elif new_skeleton:
            return jsonify({
                'success': False,
                'error': new_skeleton.error_details or 'Erro ao regenerar esqueleto'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível regenerar o esqueleto'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-upload')
def test_upload():
    """Página de teste para upload de arquivos"""
    return render_template('test_upload.html')

@app.route('/api/extract-colors', methods=['POST'])
def api_extract_colors():
    """API para extrair cores de uma imagem"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Nenhuma imagem enviada'}), 400
        
        file = request.files['image']
        if not file.filename:
            return jsonify({'error': 'Arquivo vazio'}), 400
        
        # Salvar temporariamente
        temp_url, error = image_processor.save_uploaded_file(file, prefix='temp')
        if error:
            return jsonify({'error': error}), 400
        
        # Extrair cores
        colors, error = color_extractor.extract_colors_from_logo(temp_url)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'colors': colors,
            'image_url': temp_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-connection')
def test_connection():
    """Testar conexão com banco de dados"""
    try:
        # Testar conexão
        result = db.execute_query("SELECT 1 as test")
        if result:
            return jsonify({
                'status': 'success',
                'message': '✅ Conexão com MySQL funcionando!',
                'result': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '❌ Erro na consulta SQL'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'❌ Erro de conexão: {str(e)}'
        })

@app.route('/api/requests')
def api_requests():
    """API para listar solicitações (JSON)"""
    try:
        requests = LandingPageRequest.get_all(limit=20)
        return jsonify({
            'status': 'success',
            'data': requests or []
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/regenerate-skeleton/<skeleton_id>', methods=['POST'])
def regenerate_skeleton(skeleton_id):
    """Regenerar esqueleto existente"""
    try:
        new_skeleton = skeleton_generator.regenerate_skeleton(skeleton_id)
        
        if new_skeleton and new_skeleton.status == 'completed':
            return jsonify({
                'success': True,
                'message': 'Esqueleto regenerado com sucesso!',
                'skeleton_id': new_skeleton.skeleton_id,
                'redirect_url': url_for('view_skeleton', skeleton_id=new_skeleton.skeleton_id)
            })
        elif new_skeleton:
            return jsonify({
                'success': False,
                'error': new_skeleton.error_details or 'Erro ao regenerar esqueleto'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível regenerar o esqueleto'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-skeleton/<request_id>', methods=['POST'])
def generate_skeleton(request_id):
    """Gerar esqueleto da landing page"""
    try:
        # Buscar solicitação
        request_obj = LandingPageRequest.get_by_id(request_id)
        if not request_obj:
            return jsonify({
                'success': False,
                'error': 'Solicitação não encontrada'
            })
        
        # Verificar se já não está gerando
        if request_obj.status == 'generating_skeleton':
            return jsonify({
                'success': False,
                'error': 'Esqueleto já está sendo gerado'
            })
        
        # Atualizar status para gerando
        request_obj.update_status('generating_skeleton')
        
        # Log início
        ExecutionLog.add_log(
            request_id,
            'SKELETON_GENERATION',
            'INFO',
            'Iniciando geração de esqueleto via interface web'
        )
        
        # Extrair dados de cores se existirem
        colors_data = None
        if request_obj.style_preferences_input:
            try:
                style_prefs = json.loads(request_obj.style_preferences_input)
                colors_data = style_prefs.get('brand_colors', {})
            except:
                pass
        
        # Gerar esqueleto
        skeleton = skeleton_generator.generate_skeleton(request_obj, colors_data)
        
        if skeleton and skeleton.status == 'completed':
            # Atualizar status da solicitação
            request_obj.update_status('skeleton_completed')
            
            return jsonify({
                'success': True,
                'message': 'Esqueleto gerado com sucesso!',
                'skeleton_id': skeleton.skeleton_id,
                'redirect_url': url_for('view_skeleton', skeleton_id=skeleton.skeleton_id)
            })
        else:
            # Erro na geração
            error_msg = skeleton.error_details if skeleton else 'Erro desconhecido'
            request_obj.update_status('skeleton_error', error_msg)
            
            return jsonify({
                'success': False,
                'error': error_msg
            })
            
    except Exception as e:
        # Erro interno
        ExecutionLog.add_log(
            request_id,
            'SKELETON_GENERATION',
            'ERROR',
            'Erro interno na geração de esqueleto',
            str(e)
        )
        
        # Atualizar status
        try:
            request_obj = LandingPageRequest.get_by_id(request_id)
            if request_obj:
                request_obj.update_status('system_error', str(e))
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@app.route('/view-skeleton/<skeleton_id>')
def view_skeleton(skeleton_id):
    """Visualizar esqueleto específico"""
    try:
        skeleton = GeneratedSkeleton.get_by_id(skeleton_id)
        if not skeleton:
            flash('Esqueleto não encontrado', 'error')
            return redirect(url_for('index'))
        
        # Buscar request relacionado
        request_obj = LandingPageRequest.get_by_id(skeleton.request_id)
        
        return render_template('view_skeleton.html', 
                             skeleton=skeleton,
                             request=request_obj)
    except Exception as e:
        flash(f'Erro ao carregar esqueleto: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/test-claude')
def test_claude():
    """Testar conexão com Claude API"""
    try:
        result = claude_client.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao testar Claude: {str(e)}'
        })

@app.route('/debug-config')
def debug_config():
    """Debug das configurações"""
    return jsonify({
        'claude_api_key_configured': bool(Config.CLAUDE_API_KEY and len(Config.CLAUDE_API_KEY) > 10),
        'claude_api_key_preview': Config.CLAUDE_API_KEY[:10] + '...' if Config.CLAUDE_API_KEY else 'Não configurada',
        'claude_api_url': Config.CLAUDE_API_URL,
        'db_host': Config.DB_HOST,
        'db_name': Config.DB_NAME,
        'debug_mode': Config.DEBUG
    })

@app.route('/test-claude-models')
def test_claude_models():
    """Testa diferentes modelos do Claude"""
    models_to_test = [
        "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet mais recente
        "claude-3-5-sonnet-20240620",  # Claude 3.5 Sonnet anterior
        "claude-3-sonnet-20240229",    # Claude 3 Sonnet
        "claude-3-haiku-20240307",     # Claude 3 Haiku (mais barato)
        "claude-3-opus-20240229"       # Claude 3 Opus (mais poderoso)
    ]
    
    results = {}
    
    for model in models_to_test:
        try:
            # Testar cada modelo
            payload = {
                "model": model,
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": "Responda apenas 'OK'"
                    }
                ]
            }
            
            response = requests.post(
                Config.CLAUDE_API_URL,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': Config.CLAUDE_API_KEY,
                    'anthropic-version': '2023-06-01'
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results[model] = {
                    'status': 'success',
                    'message': 'Modelo disponível'
                }
            else:
                error_data = response.json() if response.content else {}
                results[model] = {
                    'status': 'error',
                    'message': error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                }
                
        except Exception as e:
            results[model] = {
                'status': 'error',
                'message': str(e)
            }
    
    return jsonify({
        'results': results,
        'recommendation': 'Use o primeiro modelo com status success'
    })

@app.route('/update-skeleton/<skeleton_id>', methods=['POST'])
def update_skeleton(skeleton_id):
    """Atualizar dados do esqueleto"""
    try:
        skeleton = GeneratedSkeleton.get_by_id(skeleton_id)
        if not skeleton:
            return jsonify({
                'success': False,
                'error': 'Esqueleto não encontrado'
            })
        
        # Receber novos dados
        data = request.get_json()
        new_skeleton_data = data.get('skeleton_data')
        
        if not new_skeleton_data:
            return jsonify({
                'success': False,
                'error': 'Dados do esqueleto não fornecidos'
            })
        
        # Validar estrutura básica
        if not skeleton_generator._validate_skeleton_structure(new_skeleton_data):
            return jsonify({
                'success': False,
                'error': 'Estrutura do esqueleto inválida'
            })
        
        # Atualizar no banco
        query = """
        UPDATE generated_skeletons 
        SET parsed_skeleton_data = %s, status = 'user_edited'
        WHERE skeleton_id = %s
        """
        
        result = db.execute_query(query, (json.dumps(new_skeleton_data), skeleton_id))
        
        if result:
            # Log da alteração
            ExecutionLog.add_log(
                skeleton.request_id,
                'SKELETON_EDITOR',
                'INFO',
                'Esqueleto editado pelo usuário',
                json.dumps({
                    'skeleton_id': skeleton_id,
                    'sections_count': len(new_skeleton_data.get('sections', [])),
                    'edited_fields': list(new_skeleton_data.keys())
                })
            )
            
            return jsonify({
                'success': True,
                'message': 'Esqueleto atualizado com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar no banco de dados'
            })
            
    except Exception as e:
        ExecutionLog.add_log(
            skeleton.request_id if skeleton else 'unknown',
            'SKELETON_EDITOR',
            'ERROR',
            'Erro ao atualizar esqueleto',
            str(e)
        )
        
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Iniciando Landing Page Generator...")
    print("📊 Testando conexão com banco...")
    
    # Testar conexão inicial
    if db.connection:
        print("✅ Conexão com MySQL OK!")
    else:
        print("❌ Erro na conexão com MySQL!")
    
    print("📁 Verificando diretórios de upload...")
    if os.path.exists('static/uploads'):
        print("✅ Diretório de uploads OK!")
    else:
        print("❌ Erro no diretório de uploads!")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
