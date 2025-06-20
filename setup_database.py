import pymysql
from config.settings import Config

def create_database_structure():
    """Cria ou corrige a estrutura do banco de dados"""
    
    # SQL para criar/corrigir as tabelas
    tables_sql = {
        'landing_page_requests': """
        CREATE TABLE IF NOT EXISTS `landing_page_requests` (
          `request_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
          `client_id` bigint unsigned DEFAULT NULL,
          `page_title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
          `page_slug` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
          `company_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
          `company_logo_url` longtext COLLATE utf8mb4_unicode_ci,
          `main_content_brief` text COLLATE utf8mb4_unicode_ci,
          `images_input` json DEFAULT NULL,
          `sections_suggestion_input` json DEFAULT NULL,
          `style_preferences_input` json DEFAULT NULL,
          `js_requirements_input` json DEFAULT NULL,
          `status` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
          `final_html_content` longtext COLLATE utf8mb4_unicode_ci,
          `html_head` text COLLATE utf8mb4_unicode_ci,
          `html_footer` text COLLATE utf8mb4_unicode_ci,
          `final_custom_css` text COLLATE utf8mb4_unicode_ci,
          `final_javascript` text COLLATE utf8mb4_unicode_ci,
          `final_html_url` longtext COLLATE utf8mb4_unicode_ci,
          `error_message` text COLLATE utf8mb4_unicode_ci,
          `created_at` timestamp NULL DEFAULT NULL,
          `updated_at` timestamp NULL DEFAULT NULL,
          PRIMARY KEY (`request_id`),
          UNIQUE KEY `landing_page_requests_page_slug_unique` (`page_slug`),
          KEY `landing_page_requests_status_index` (`status`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'generated_skeletons': """
        CREATE TABLE IF NOT EXISTS `generated_skeletons` (
          `skeleton_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `request_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `raw_skeleton_response_from_ai` longtext COLLATE utf8mb4_unicode_ci,
          `parsed_skeleton_data` json DEFAULT NULL,
          `prompt_tokens_phase1` int NOT NULL DEFAULT '0',
          `completion_tokens_phase1` int NOT NULL DEFAULT '0',
          `duration_ms_phase1` int NOT NULL DEFAULT '0',
          `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
          `error_details` text COLLATE utf8mb4_unicode_ci,
          `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`skeleton_id`),
          KEY `generated_skeletons_request_id_index` (`request_id`),
          KEY `generated_skeletons_status_index` (`status`),
          CONSTRAINT `generated_skeletons_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `landing_page_requests` (`request_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'generated_html_sections': """
        CREATE TABLE IF NOT EXISTS `generated_html_sections` (
          `html_section_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `request_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `section_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
          `section_order` int NOT NULL,
          `input_text_for_html` text COLLATE utf8mb4_unicode_ci,
          `generated_html_snippet` longtext COLLATE utf8mb4_unicode_ci,
          `raw_html_response_from_ai` longtext COLLATE utf8mb4_unicode_ci,
          `prompt_tokens_phase2` int NOT NULL DEFAULT '0',
          `completion_tokens_phase2` int NOT NULL DEFAULT '0',
          `duration_ms_phase2` int NOT NULL DEFAULT '0',
          `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
          `error_details` text COLLATE utf8mb4_unicode_ci,
          `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`html_section_id`),
          KEY `generated_html_sections_request_id_index` (`request_id`),
          KEY `generated_html_sections_section_order_index` (`section_order`),
          KEY `generated_html_sections_status_index` (`status`),
          CONSTRAINT `generated_html_sections_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `landing_page_requests` (`request_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        'execution_logs': """
        CREATE TABLE IF NOT EXISTS `execution_logs` (
          `log_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `request_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
          `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          `component` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
          `log_level` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
          `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
          `details` longtext COLLATE utf8mb4_unicode_ci,
          PRIMARY KEY (`log_id`),
          KEY `execution_logs_request_id_index` (`request_id`),
          KEY `execution_logs_timestamp_index` (`timestamp`),
          KEY `execution_logs_log_level_index` (`log_level`),
          CONSTRAINT `execution_logs_request_id_foreign` FOREIGN KEY (`request_id`) REFERENCES `landing_page_requests` (`request_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    }
    
    try:
        # Conectar ao banco
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        
        print("🔧 Verificando e corrigindo estrutura do banco...")
        
        with connection.cursor() as cursor:
            # Desabilitar verificação de chaves estrangeiras temporariamente
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Criar cada tabela
            for table_name, sql in tables_sql.items():
                try:
                    print(f"📋 Criando/verificando tabela: {table_name}")
                    cursor.execute(sql)
                    print(f"✅ Tabela {table_name} OK!")
                except Exception as e:
                    print(f"❌ Erro na tabela {table_name}: {e}")
            
            # Reabilitar verificação de chaves estrangeiras
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.close()
        print("✅ Estrutura do banco corrigida com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir estrutura do banco: {e}")
        return False

def verify_table_structure():
    """Verifica se as tabelas têm as colunas corretas"""
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar estrutura da tabela principal
            cursor.execute("DESCRIBE landing_page_requests")
            columns = cursor.fetchall()
            
            print("📊 Estrutura da tabela landing_page_requests:")
            for col in columns:
                print(f"  - {col['Field']} ({col['Type']})")
            
            # Verificar se client_id existe
            column_names = [col['Field'] for col in columns]
            if 'client_id' in column_names:
                print("✅ Coluna client_id encontrada!")
                return True
            else:
                print("❌ Coluna client_id NÃO encontrada!")
                return False
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando correção do banco de dados...")
    
    # Verificar estrutura atual
    print("\n1️⃣ Verificando estrutura atual...")
    verify_table_structure()
    
    # Corrigir estrutura
    print("\n2️⃣ Corrigindo estrutura...")
    if create_database_structure():
        print("\n3️⃣ Verificando correção...")
        verify_table_structure()
        print("\n🎉 Banco pronto para uso!")
    else:
        print("\n❌ Falha na correção do banco")