CREATE TABLE `landing_page_requests` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--

DROP TABLE IF EXISTS `generated_skeletons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generated_skeletons` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `generated_html_sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generated_html_sections` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `execution_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `execution_logs` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `clients_email_unique` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
DROP TABLE IF EXISTS `api_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `api_keys` (
  `id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_keys_key_unique` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Dumping data for table `api_keys`
--


LOCK TABLES `api_keys` WRITE;
/*!40000 ALTER TABLE `api_keys` DISABLE KEYS */;
INSERT INTO `api_keys` VALUES ('f8e8b91a-41f2-11f0-826d-00505651d6f2','futeboldorei_api_key_123456','API Key Inicial',1,'2025-06-05 12:53:46','2025-06-05 12:53:46');
/*!40000 ALTER TABLE `api_keys` ENABLE KEYS */;
UNLOCK TABLES;



CREATE TABLE `clients` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `clients_email_unique` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

