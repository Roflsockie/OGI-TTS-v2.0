import os
import sys
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

class HelpTabManager:
    """Manager for Help tab functionality with API registration guides"""

    def __init__(self, main_window):
        self.main_window = main_window
        # Connect to theme changes
        if hasattr(self.main_window, 'themeComboBox'):
            self.main_window.themeComboBox.currentTextChanged.connect(self.on_theme_changed)

    def setup_ui(self):
        """Setup UI for help tab - alias for setup_help_ui for consistency"""
        self.setup_help_ui()

    def setup_help_ui(self):
        """Setup help UI elements from Qt Designer"""
        try:
            # Connect signals for help elements
            if hasattr(self.main_window, 'helpGuideComboBox'):
                # Update guide list based on current language
                self.update_guide_list()
                self.main_window.helpGuideComboBox.currentTextChanged.connect(self.update_help_content)

            # Connect to language changes to update guide list
            if hasattr(self.main_window, 'languageComboBox'):
                self.main_window.languageComboBox.currentTextChanged.connect(self.on_language_changed)

            # Load initial content
            self.update_help_content("Выберите гайд...")

        except Exception as e:
            print(f"Help UI setup error: {e}")

    def update_guide_list(self):
        """Update the guide list based on current interface language"""
        if not hasattr(self.main_window, 'helpGuideComboBox'):
            return

        current_language = self.get_current_language()

        if current_language == "English":
            guides = [
                "Select a guide...",
                "Google OCR API (en)",
                "Google Translate API (en)",
                "Azure OCR API (en)",
                "Azure Translate API (en)",
                "App Features (en)"
            ]
        elif current_language == "Українська":
            guides = [
                "Оберіть гайд...",
                "Google OCR API (ua)",
                "Google Translate API (ua)",
                "Azure OCR API (ua)",
                "Azure Translate API (ua)",
                "Функції додатку (ua)"
            ]
        else:  # Russian (default)
            guides = [
                "Выберите гайд...",
                "Google OCR API (ru)",
                "Google Translate API (ru)",
                "Azure OCR API (ru)",
                "Azure Translate API (ru)",
                "Функции программы (ru)"
            ]

        self.main_window.helpGuideComboBox.clear()
        self.main_window.helpGuideComboBox.addItems(guides)

    def get_current_language(self):
        """Get current interface language"""
        if hasattr(self.main_window, 'languageComboBox'):
            return self.main_window.languageComboBox.currentText()
        return "Русский"  # Default fallback

    def on_theme_changed(self):
        """Handle theme change by updating help content"""
        current_guide = "Выберите гайд..."
        if hasattr(self.main_window, 'helpGuideComboBox'):
            current_guide = self.main_window.helpGuideComboBox.currentText()
        self.update_help_content(current_guide)

    def on_language_changed(self):
        """Handle language change by updating guide list and content"""
        # Update the guide list for the new language
        self.update_guide_list()
        
        # Update content to match the new language
        current_guide = self.get_default_guide_for_language()
        self.update_help_content(current_guide)

    def get_default_guide_for_language(self):
        """Get the default guide name for current language"""
        current_language = self.get_current_language()
        if current_language == "English":
            return "Select a guide..."
        elif current_language == "Українська":
            return "Оберіть гайд..."
        else:
            return "Выберите гайд..."

    def update_help_content(self, guide_name):
        """Update the help content display with the selected guide"""
        try:
            content = self.get_guide_content(guide_name)
            if hasattr(self.main_window, 'helpContentBrowser'):
                self.main_window.helpContentBrowser.setHtml(content)
        except Exception as e:
            print(f"Error updating help content: {e}")

    def get_current_theme(self):
        """Get current theme name"""
        if hasattr(self.main_window, 'themeComboBox'):
            return self.main_window.themeComboBox.currentText()
        return "Default"

    def is_dark_theme(self):
        """Check if current theme is dark"""
        return self.get_current_theme() == "OgiDark"

    def get_guide_content(self, guide_name):
        """Get HTML content for the selected guide"""
        # Get current language
        current_language = self.get_current_language()
        
        # Map language to directory
        lang_dirs = {
            "Русский": "ru",
            "English": "en", 
            "Українська": "ua"
        }
        lang_dir = lang_dirs.get(current_language, "ru")  # Default to Russian
        
        # Map guide names to file names (same for all languages)
        file_mapping = {
            "Выберите гайд...": "welcome.html",
            "Select a guide...": "welcome.html",
            "Оберіть гайд...": "welcome.html",
            "Google OCR API (ru)": "google_ocr.html",
            "Google OCR API (en)": "google_ocr.html",
            "Google OCR API (ua)": "google_ocr.html",
            "Google Translate API (ru)": "google_translate.html",
            "Google Translate API (en)": "google_translate.html",
            "Google Translate API (ua)": "google_translate.html",
            "Azure OCR API (ru)": "azure_ocr.html",
            "Azure OCR API (en)": "azure_ocr.html",
            "Azure OCR API (ua)": "azure_ocr.html",
            "Azure Translate API (ru)": "azure_translate.html",
            "Azure Translate API (en)": "azure_translate.html",
            "Azure Translate API (ua)": "azure_translate.html",
            "Функции программы (ru)": "app_features.html",
            "App Features (en)": "app_features.html",
            "Функції додатку (ua)": "app_features.html"
        }

        filename = file_mapping.get(guide_name)
        if filename:
            try:
                guides_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'guides')
                lang_guides_dir = os.path.join(guides_dir, lang_dir)
                filepath = os.path.join(lang_guides_dir, filename)
                
                # If language-specific file doesn't exist, try root guides directory (fallback to Russian)
                if not os.path.exists(filepath):
                    filepath = os.path.join(guides_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply theme colors to HTML content
                content = self.apply_theme_colors_to_html(content)
                
                return content
            except Exception as e:
                print(f"Error loading guide file {filename} for language {lang_dir}: {e}")
                return self.get_fallback_content(guide_name)

        return self.get_fallback_content(guide_name)

    def get_fallback_content(self, guide_name):
        """Fallback content generation if file loading fails"""
        current_language = self.get_current_language()
        
        if current_language == "English":
            return self.get_welcome_content_en()
        elif current_language == "Українська":
            return self.get_welcome_content_ua()
        else:  # Russian (default)
            return self.get_welcome_content()

    def get_welcome_content(self):
        """Welcome content for help tab"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        accent_color = "#61DAFB" if is_dark else "#2E86C1"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: {accent_color}; }}
                .welcome {{ text-align: center; margin: 50px 0; }}
                .icon {{ font-size: 48px; margin: 20px; }}
            </style>
        </head>
        <body>
            <div class="welcome">
                <div class="icon">📚</div>
                <h1>Добро пожаловать в справку OGI TTS!</h1>
                <p>Выберите интересующий вас гайд из списка выше для получения подробных инструкций по настройке API ключей.</p>
                <p>Здесь вы найдете пошаговые руководства по регистрации и настройке всех поддерживаемых сервисов.</p>
            </div>
        </body>
        </html>
        """

    def get_google_ocr_guide(self):
        """Google Vision API setup guide"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        step_bg = "#3C3C3C" if is_dark else "#F8F9FA"
        warning_bg = "#4A4A2A" if is_dark else "#FFF3CD"
        warning_border = "#666633" if is_dark else "#FFEAA7"
        code_bg = "#4A4A4A" if is_dark else "#E8F0FE"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: #4285F4; border-bottom: 2px solid #4285F4; padding-bottom: 10px; }}
                h2 {{ color: #34A853; margin-top: 30px; }}
                .step {{ background: {step_bg}; padding: 15px; margin: 10px 0; border-left: 4px solid #4285F4; }}
                .step-number {{ font-weight: bold; color: #4285F4; font-size: 18px; }}
                .warning {{ background: {warning_bg}; border: 1px solid {warning_border}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .link {{ color: #4285F4; text-decoration: none; font-weight: bold; }}
                .link:hover {{ text-decoration: underline; }}
                .code {{ background: {code_bg}; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>🔍 Настройка Google OCR API</h1>

            <div class="warning">
                ⚠️ <strong>Важно:</strong> Google Vision API платный сервис. Первые 1000 запросов в месяц бесплатны, далее ~$1.50 за 1000 изображений.
            </div>

            <h2>📋 Шаг 1: Создание Google Cloud проекта</h2>
            <div class="step">
                <span class="step-number">1.1</span> Перейдите на <a href="https://console.cloud.google.com/" class="link">Google Cloud Console</a>
                <br><span class="step-number">1.2</span> Создайте новый проект или выберите существующий
                <br><span class="step-number">1.3</span> Включите биллинг (платежный аккаунт) для проекта
            </div>

            <h2>🎯 Шаг 2: Включение Vision API</h2>
            <div class="step">
                <span class="step-number">2.1</span> В меню слева выберите "APIs & Services" → "Library"
                <br><span class="step-number">2.2</span> Найдите "Cloud Vision API" и нажмите "Enable"
                <br><span class="step-number">2.3</span> Дождитесь активации сервиса
            </div>

            <h2>🔑 Шаг 3: Создание API ключа</h2>
            <div class="step">
                <span class="step-number">3.1</span> Перейдите в "APIs & Services" → "Credentials"
                <br><span class="step-number">3.2</span> Нажмите "Create Credentials" → "API key"
                <br><span class="step-number">3.3</span> Скопируйте созданный API ключ
                <br><span class="step-number">3.4</span> <strong>Ограничьте ключ:</strong> нажмите на ключ → "Restrict key" → выберите "Cloud Vision API"
            </div>

            <h2>⚙️ Шаг 4: Настройка в OGI TTS</h2>
            <div class="step">
                <span class="step-number">4.1</span> В приложении перейдите в вкладку "IMG to Text"
                <br><span class="step-number">4.2</span> Выберите "Google Vision API" в выпадающем списке
                <br><span class="step-number">4.3</span> Вставьте API ключ в поле "API Key"
                <br><span class="step-number">4.4</span> Проверьте статус иконки (должна появиться ✅)
            </div>

            <h2>💡 Советы</h2>
            <ul>
                <li>API ключ можно использовать для распознавания текста на изображениях</li>
                <li>Поддерживаемые форматы: PNG, JPG, JPEG, BMP, TIFF, WebP</li>
                <li>Максимальный размер файла: 20MB</li>
                <li>Бесплатный лимит: 1000 запросов/месяц</li>
            </ul>

            <h2>🔗 Полезные ссылки</h2>
            <ul>
                <li><a href="https://console.cloud.google.com/" class="link">Google Cloud Console</a></li>
                <li><a href="https://cloud.google.com/vision/docs" class="link">Документация Vision API</a></li>
                <li><a href="https://cloud.google.com/pricing" class="link">Цены на сервисы</a></li>
            </ul>
        </body>
        </html>
        """

    def get_azure_translate_guide(self):
        """Azure Translator API setup guide"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        step_bg = "#3C3C3C" if is_dark else "#F8F9FA"
        warning_bg = "#4A4A2A" if is_dark else "#FFF3CD"
        warning_border = "#666633" if is_dark else "#FFEAA7"
        code_bg = "#4A4A4A" if is_dark else "#E8F0FE"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px; }}
                h2 {{ color: #107C10; margin-top: 30px; }}
                .step {{ background: {step_bg}; padding: 15px; margin: 10px 0; border-left: 4px solid #0078D4; }}
                .step-number {{ font-weight: bold; color: #0078D4; font-size: 18px; }}
                .warning {{ background: {warning_bg}; border: 1px solid {warning_border}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .link {{ color: #0078D4; text-decoration: none; font-weight: bold; }}
                .link:hover {{ text-decoration: underline; }}
                .code {{ background: {code_bg}; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>🌐 Настройка Azure Translate API</h1>

            <div class="warning">
                ⚠️ <strong>Важно:</strong> Azure Translator имеет бесплатный tier с ограничениями. Для продакшена рассмотрите платные планы.
            </div>

            <h2>📋 Шаг 1: Создание Azure аккаунта</h2>
            <div class="step">
                <span class="step-number">1.1</span> Перейдите на <a href="https://portal.azure.com/" class="link">Azure Portal</a>
                <br><span class="step-number">1.2</span> Создайте бесплатный аккаунт или войдите в существующий
                <br><span class="step-number">1.3</span> Настройте платежный метод (для бесплатного tier не обязательно)
            </div>

            <h2>🎯 Шаг 2: Создание Cognitive Services ресурса</h2>
            <div class="step">
                <span class="step-number">2.1</span> В поиске найдите "Cognitive Services" и выберите
                <br><span class="step-number">2.2</span> Нажмите "Create" → "Translator"
                <br><span class="step-number">2.3</span> Заполните:
                <ul>
                    <li>Subscription: выберите подписку</li>
                    <li>Resource group: создайте новую или выберите существующую</li>
                    <li>Region: East US или ближайший регион</li>
                    <li>Name: уникальное имя ресурса</li>
                    <li>Pricing tier: Free F0 (2M символов бесплатно)</li>
                </ul>
            </div>

            <h2>🔑 Шаг 3: Получение API ключей</h2>
            <div class="step">
                <span class="step-number">3.1</span> После создания ресурса перейдите к нему
                <br><span class="step-number">3.2</span> В меню слева выберите "Keys and Endpoint"
                <br><span class="step-number">3.3</span> Скопируйте KEY 1 или KEY 2
                <br><span class="step-number">3.4</span> Также скопируйте "Location/Region" (например: "eastus")
            </div>

            <h2>⚙️ Шаг 4: Настройка в OGI TTS</h2>
            <div class="step">
                <span class="step-number">4.1</span> В приложении перейдите в вкладку "Settings"
                <br><span class="step-number">4.2</span> Выберите "Microsoft Translator" в выпадающем списке
                <br><span class="step-number">4.3</span> Вставьте API ключ в поле "API Key"
                <br><span class="step-number">4.4</span> Проверьте статус иконки (должна появиться ✅)
            </div>

            <h2>💡 Советы</h2>
            <ul>
                <li>Бесплатный tier: 2 миллиона символов в месяц</li>
                <li>Поддержка 70+ языков</li>
                <li>Высокая точность перевода</li>
                <li>Интеграция с Azure экосистемой</li>
            </ul>

            <h2>🔗 Полезные ссылки</h2>
            <ul>
                <li><a href="https://portal.azure.com/" class="link">Azure Portal</a></li>
                <li><a href="https://docs.microsoft.com/en-us/azure/cognitive-services/translator/" class="link">Документация Translator</a></li>
                <li><a href="https://azure.microsoft.com/en-us/pricing/details/cognitive-services/translator/" class="link">Цены</a></li>
            </ul>
        </body>
        </html>
        """

    def get_google_translate_guide(self):
        """Google Cloud Translate API setup guide"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        step_bg = "#3C3C3C" if is_dark else "#F8F9FA"
        warning_bg = "#4A4A2A" if is_dark else "#FFF3CD"
        warning_border = "#666633" if is_dark else "#FFEAA7"
        code_bg = "#4A4A4A" if is_dark else "#E8F0FE"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: #4285F4; border-bottom: 2px solid #4285F4; padding-bottom: 10px; }}
                h2 {{ color: #34A853; margin-top: 30px; }}
                .step {{ background: {step_bg}; padding: 15px; margin: 10px 0; border-left: 4px solid #4285F4; }}
                .step-number {{ font-weight: bold; color: #4285F4; font-size: 18px; }}
                .warning {{ background: {warning_bg}; border: 1px solid {warning_border}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .link {{ color: #4285F4; text-decoration: none; font-weight: bold; }}
                .link:hover {{ text-decoration: underline; }}
                .code {{ background: {code_bg}; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>🌍 Настройка Google Cloud Translate API</h1>

            <div class="warning">
                ⚠️ <strong>Важно:</strong> Требуется платежный аккаунт Google Cloud. Первые 500k символов бесплатны ежемесячно.
            </div>

            <h2>📋 Шаг 1: Создание Google Cloud проекта</h2>
            <div class="step">
                <span class="step-number">1.1</span> Перейдите на <a href="https://console.cloud.google.com/" class="link">Google Cloud Console</a>
                <br><span class="step-number">1.2</span> Создайте новый проект или выберите существующий
                <br><span class="step-number">1.3</span> Убедитесь, что биллинг включен
            </div>

            <h2>🎯 Шаг 2: Включение Translation API</h2>
            <div class="step">
                <span class="step-number">2.1</span> В меню слева выберите "APIs & Services" → "Library"
                <br><span class="step-number">2.2</span> Найдите "Cloud Translation API" и нажмите "Enable"
                <br><span class="step-number">2.3</span> Дождитесь активации (может занять несколько минут)
            </div>

            <h2>🔑 Шаг 3: Создание сервисного аккаунта</h2>
            <div class="step">
                <span class="step-number">3.1</span> Перейдите в "IAM & Admin" → "Service Accounts"
                <br><span class="step-number">3.2</span> Нажмите "Create Service Account"
                <br><span class="step-number">3.3</span> Заполните имя и описание
                <br><span class="step-number">3.4</span> Назначьте роль "Cloud Translation API User"
                <br><span class="step-number">3.5</span> Создайте JSON-ключ для аккаунта
            </div>

            <h2>⚙️ Шаг 4: Настройка в OGI TTS</h2>
            <div class="step">
                <span class="step-number">4.1</span> В приложении перейдите в вкладку "Settings"
                <br><span class="step-number">4.2</span> Выберите "Google Cloud Translate API"
                <br><span class="step-number">4.3</span> Вставьте содержимое JSON-файла ключа в поле "API Key"
                <br><span class="step-number">4.4</span> Проверьте статус иконки (должна появиться ✅)
            </div>

            <h2>💡 Советы</h2>
            <ul>
                <li>Используйте сервисный аккаунт вместо API ключа для безопасности</li>
                <li>Бесплатный лимит: 500k символов/месяц</li>
                <li>Поддержка 100+ языков</li>
                <li>Высокая скорость и точность перевода</li>
            </ul>

            <h2>🔗 Полезные ссылки</h2>
            <ul>
                <li><a href="https://console.cloud.google.com/" class="link">Google Cloud Console</a></li>
                <li><a href="https://cloud.google.com/translate/docs" class="link">Документация Translate API</a></li>
                <li><a href="https://cloud.google.com/pricing" class="link">Цены на сервисы</a></li>
            </ul>
        </body>
        </html>
        """

    def get_azure_ocr_guide(self):
        """Azure Computer Vision API setup guide"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        step_bg = "#3C3C3C" if is_dark else "#F8F9FA"
        warning_bg = "#4A4A2A" if is_dark else "#FFF3CD"
        warning_border = "#666633" if is_dark else "#FFEAA7"
        code_bg = "#4A4A4A" if is_dark else "#E8F0FE"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 10px; }}
                h2 {{ color: #107C10; margin-top: 30px; }}
                .step {{ background: {step_bg}; padding: 15px; margin: 10px 0; border-left: 4px solid #0078D4; }}
                .step-number {{ font-weight: bold; color: #0078D4; font-size: 18px; }}
                .warning {{ background: {warning_bg}; border: 1px solid {warning_border}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .link {{ color: #0078D4; text-decoration: none; font-weight: bold; }}
                .link:hover {{ text-decoration: underline; }}
                .code {{ background: {code_bg}; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>👁️ Настройка Azure OCR API</h1>

            <div class="warning">
                ⚠️ <strong>Важно:</strong> Azure Computer Vision имеет бесплатный tier с ограничениями по количеству запросов.
            </div>

            <h2>📋 Шаг 1: Создание Azure аккаунта</h2>
            <div class="step">
                <span class="step-number">1.1</span> Перейдите на <a href="https://portal.azure.com/" class="link">Azure Portal</a>
                <br><span class="step-number">1.2</span> Создайте бесплатный аккаунт или войдите в существующий
            </div>

            <h2>🎯 Шаг 2: Создание Computer Vision ресурса</h2>
            <div class="step">
                <span class="step-number">2.1</span> В поиске найдите "Computer Vision" и выберите
                <br><span class="step-number">2.2</span> Нажмите "Create" → "Computer Vision"
                <br><span class="step-number">2.3</span> Заполните:
                <ul>
                    <li>Subscription: выберите подписку</li>
                    <li>Resource group: создайте новую или выберите существующую</li>
                    <li>Region: East US или ближайший регион</li>
                    <li>Name: уникальное имя ресурса</li>
                    <li>Pricing tier: Free F0 (20 запросов/минута, 5000/месяц)</li>
                </ul>
            </div>

            <h2>🔑 Шаг 3: Получение API ключей</h2>
            <div class="step">
                <span class="step-number">3.1</span> После создания ресурса перейдите к нему
                <br><span class="step-number">3.2</span> В меню слева выберите "Keys and Endpoint"
                <br><span class="step-number">3.3</span> Скопируйте KEY 1 или KEY 2
                <br><span class="step-number">3.4</span> Скопируйте "Endpoint" URL
            </div>

            <h2>⚙️ Шаг 4: Настройка в OGI TTS</h2>
            <div class="step">
                <span class="step-number">4.1</span> В приложении перейдите в вкладку "IMG to Text"
                <br><span class="step-number">4.2</span> Выберите "Azure Computer Vision" в выпадающем списке
                <br><span class="step-number">4.3</span> Вставьте API ключ в поле "API Key"
                <br><span class="step-number">4.4</span> Проверьте статус иконки (должна появиться ✅)
            </div>

            <h2>💡 Советы</h2>
            <ul>
                <li>Бесплатный tier: 5000 запросов/месяц</li>
                <li>Поддержка OCR для 25+ языков</li>
                <li>Дополнительные возможности: анализ изображений, распознавание лиц</li>
                <li>Интеграция с Azure экосистемой</li>
            </ul>

            <h2>🔗 Полезные ссылки</h2>
            <ul>
                <li><a href="https://portal.azure.com/" class="link">Azure Portal</a></li>
                <li><a href="https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/" class="link">Документация Computer Vision</a></li>
                <li><a href="https://azure.microsoft.com/en-us/pricing/details/cognitive-services/computer-vision/" class="link">Цены</a></li>
            </ul>
        </body>
        </html>
        """

    def get_app_features_guide(self):
        """App features and functionality guide"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        feature_bg = "#3C3C3C" if is_dark else "#E8F5E8"
        tab_bg = "#4A4A2A" if is_dark else "#FFF3CD"
        tab_border = "#666633" if is_dark else "#FFEAA7"
        file_bg = "#2A4A4A" if is_dark else "#F0F8FF"
        code_bg = "#4A4A4A" if is_dark else "#F5F5F5"
        important_bg = "#4A4A2A" if is_dark else "#FFEAA7"
        important_border = "#666633" if is_dark else "#D4AC0D"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: #FF6B35; border-bottom: 2px solid #FF6B35; padding-bottom: 10px; }}
                h2 {{ color: #2E86C1; margin-top: 30px; }}
                .feature {{ background: {feature_bg}; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                .tab-section {{ background: {tab_bg}; border: 1px solid {tab_border}; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .tab-title {{ font-weight: bold; color: #FF6B35; font-size: 18px; margin-bottom: 10px; }}
                .file-info {{ background: {file_bg}; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .code {{ background: {code_bg}; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
                .important {{ background: {important_bg}; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid {important_border}; }}
            </style>
        </head>
        <body>
            <h1>� Функции программы OGI TTS</h1>

            <div class="important">
                <strong>OGI TTS</strong> - это многофункциональный инструмент для работы с текстом и речью, поддерживающий различные языки и форматы.
            </div>

            <h2>� Основные вкладки и их функции</h2>

            <div class="tab-section">
                <div class="tab-title">🎯 General (Главная)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>🎤 <strong>Text-to-Speech:</strong> Преобразование текста в речь</li>
                    <li>📂 <strong>Import Text:</strong> Загрузка текста из файлов (.txt, .docx)</li>
                    <li>▶️ <strong>Play Audio:</strong> Прослушивание сгенерированной речи</li>
                    <li>💾 <strong>Save Audio:</strong> Сохранение аудио в папку tts_audio</li>
                    <li>🌐 <strong>Translation:</strong> Перевод текста между языками</li>
                </ul>
                <div class="file-info">
                    <strong>📍 Сохранение:</strong> Аудиофайлы сохраняются в папку <code>tts_audio/</code> с именами типа <code>ru_output_edgezira.wav</code>
                </div>
            </div>

            <div class="tab-section">
                <div class="tab-title">📊 Batch Processing (Пакетная обработка)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>📁 <strong>Import Multiple Files:</strong> Загрузка нескольких файлов одновременно</li>
                    <li>🔄 <strong>Batch Conversion:</strong> Пакетное преобразование текста в речь</li>
                    <li>📋 <strong>Queue Management:</strong> Управление очередью задач</li>
                    <li>📈 <strong>Progress Tracking:</strong> Отслеживание прогресса обработки</li>
                </ul>
                <div class="file-info">
                    <strong>� Сохранение:</strong> Каждый файл сохраняется отдельно в папку <code>tts_audio/</code> с уникальными именами
                </div>
            </div>

            <div class="tab-section">
                <div class="tab-title">🖼️ IMG to Text (Изображение в текст)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>📷 <strong>OCR Processing:</strong> Распознавание текста на изображениях</li>
                    <li>🔧 <strong>API Integration:</strong> Поддержка Google Vision и Azure Computer Vision</li>
                    <li>📄 <strong>Multiple Formats:</strong> Поддержка PNG, JPG, JPEG, BMP, TIFF, WebP</li>
                    <li>🌍 <strong>Multi-language:</strong> Распознавание текста на разных языках</li>
                </ul>
                <div class="file-info">
                    <strong>📍 Сохранение:</strong> Распознанный текст можно скопировать или использовать для дальнейшей обработки
                </div>
            </div>

            <div class="tab-section">
                <div class="tab-title">⚙️ Settings (Настройки)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>🎨 <strong>Theme Selection:</strong> Выбор темы интерфейса (Default, OgiDark)</li>
                    <li>🌐 <strong>Language:</strong> Выбор языка интерфейса (English, Русский, Українська)</li>
                    <li>🔑 <strong>API Keys:</strong> Настройка ключей для переводов и OCR</li>
                    <li>🎵 <strong>Voice Settings:</strong> Настройка параметров голоса (скорость, громкость, тон)</li>
                </ul>
            </div>

            <div class="tab-section">
                <div class="tab-title">📋 Log (Журнал)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>📝 <strong>Operation Log:</strong> Журнал всех операций программы</li>
                    <li>📋 <strong>Copy Log:</strong> Копирование журнала в буфер обмена</li>
                    <li>🗑️ <strong>Clear Log:</strong> Очистка журнала</li>
                    <li>🎨 <strong>Color Coding:</strong> Цветовая индикация типов сообщений</li>
                </ul>
            </div>

            <div class="tab-section">
                <div class="tab-title">❓ Help (Справка)</div>
                <p><strong>Функции:</strong></p>
                <ul>
                    <li>📚 <strong>API Guides:</strong> Подробные инструкции по настройке API</li>
                    <li>🔗 <strong>External Links:</strong> Ссылки на документацию провайдеров</li>
                    <li>💡 <strong>Tips & Tricks:</strong> Советы по использованию</li>
                    <li>🚀 <strong>Feature Overview:</strong> Описание всех функций программы</li>
                </ul>
            </div>

            <h2>� Работа с файлами</h2>

            <div class="feature">
                <h3>📥 Импорт документов</h3>
                <ul>
                    <li><strong>Поддерживаемые форматы:</strong> .txt, .docx</li>
                    <li><strong>Кодировка:</strong> UTF-8 (рекомендуется)</li>
                    <li><strong>Максимальный размер:</strong> Ограничен памятью системы</li>
                    <li><strong>Пакетная обработка:</strong> До 100+ файлов одновременно</li>
                </ul>
            </div>

            <div class="feature">
                <h3>📤 Экспорт аудио</h3>
                <ul>
                    <li><strong>Формат:</strong> WAV (высокое качество)</li>
                    <li><strong>Папка сохранения:</strong> <code>tts_audio/</code></li>
                    <li><strong>Именование:</strong> <code>язык_output_модельголос.wav</code></li>
                    <li><strong>Примеры:</strong> <code>ru_output_edgezira.wav</code>, <code>en_output_edgearia.wav</code></li>
                </ul>
            </div>

            <h2>🎵 Настройки голоса</h2>

            <div class="feature">
                <h3>Параметры синтеза речи</h3>
                <ul>
                    <li><strong>Скорость:</strong> 0.5x - 2.0x (регулируется слайдером)</li>
                    <li><strong>Громкость:</strong> 0% - 100% (регулируется слайдером)</li>
                    <li><strong>Тон:</strong> -50Hz - +50Hz (регулируется слайдером)</li>
                    <li><strong>Голоса:</strong> Male/Female для каждого языка</li>
                    <li><strong>Языки:</strong> English, Russian, Ukrainian, Japanese</li>
                </ul>
            </div>

            <h2>� Системные требования</h2>

            <div class="feature">
                <h3>Минимальные требования</h3>
                <ul>
                    <li><strong>ОС:</strong> Windows 10/11</li>
                    <li><strong>Python:</strong> 3.8+</li>
                    <li><strong>Память:</strong> 4GB RAM</li>
                    <li><strong>Место на диске:</strong> 500MB</li>
                    <li><strong>Интернет:</strong> Для API функций</li>
                </ul>
            </div>

            <h2>🚀 Быстрый старт</h2>

            <div class="important">
                <ol>
                    <li><strong>Установите зависимости:</strong> <code>pip install -r requirements.txt</code></li>
                    <li><strong>Запустите программу:</strong> <code>python main.py</code></li>
                    <li><strong>Выберите язык и голос</strong> в выпадающих списках</li>
                    <li><strong>Введите текст</strong> или импортируйте файл</li>
                    <li><strong>Нажмите "Play"</strong> для прослушивания или "Save" для сохранения</li>
                </ol>
            </div>

        </body>
        </html>
        """

    def get_welcome_content_en(self):
        """Welcome content for help tab in English"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        accent_color = "#61DAFB" if is_dark else "#2E86C1"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: {accent_color}; }}
                .welcome {{ text-align: center; margin: 50px 0; }}
                .icon {{ font-size: 48px; margin: 20px; }}
            </style>
        </head>
        <body>
            <div class="welcome">
                <div class="icon">📚</div>
                <h1>Welcome to OGI TTS Help!</h1>
                <p>Select a guide from the list above to get detailed instructions on setting up API keys.</p>
                <p>Here you will find step-by-step guides for registering and configuring all supported services.</p>
            </div>
        </body>
        </html>
        """

    def get_welcome_content_ua(self):
        """Welcome content for help tab in Ukrainian"""
        is_dark = self.is_dark_theme()
        bg_color = "#2B2B2B" if is_dark else "#FFFFFF"
        text_color = "#FFFFFF" if is_dark else "#000000"
        accent_color = "#61DAFB" if is_dark else "#2E86C1"

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1 {{ color: {accent_color}; }}
                .welcome {{ text-align: center; margin: 50px 0; }}
                .icon {{ font-size: 48px; margin: 20px; }}
            </style>
        </head>
        <body>
            <div class="welcome">
                <div class="icon">📚</div>
                <h1>Ласкаво просимо до довідки OGI TTS!</h1>
                <p>Оберіть гайд зі списку вище, щоб отримати детальні інструкції з налаштування API ключів.</p>
                <p>Тут ви знайдете покрокові керівництва з реєстрації та налаштування всіх підтримуваних сервісів.</p>
            </div>
        </body>
        </html>
        """
    
    def apply_theme_colors_to_html(self, html_content):
        """Apply current theme colors to HTML content"""
        is_dark = self.is_dark_theme()
        
        if is_dark:
            # Dark theme colors
            bg_color = "#2B2B2B"
            text_color = "#FFFFFF"
            step_bg = "#3C3C3C"
            warning_bg = "#4A4A2A"
            warning_border = "#666633"
            code_bg = "#4A4A4A"
            tab_bg = "#4A4A2A"
            tab_border = "#666633"
            file_bg = "#2A4A4A"
            important_bg = "#4A4A2A"
            important_border = "#666633"
        else:
            # Light theme colors (original)
            bg_color = "#FFFFFF"
            text_color = "#000000"
            step_bg = "#F8F9FA"
            warning_bg = "#FFF3CD"
            warning_border = "#FFEAA7"
            code_bg = "#E8F0FE"
            tab_bg = "#FFF3CD"
            tab_border = "#FFEAA7"
            file_bg = "#F0F8FF"
            important_bg = "#FFEAA7"
            important_border = "#D4AC0D"
        
        # Replace main body colors
        html_content = html_content.replace('background-color: #FFFFFF', f'background-color: {bg_color}')
        html_content = html_content.replace('background-color:#FFFFFF', f'background-color:{bg_color}')
        html_content = html_content.replace('color: #000000', f'color: {text_color}')
        html_content = html_content.replace('color:#000000', f'color:{text_color}')
        
        # Replace step block backgrounds
        html_content = html_content.replace('background: #F8F9FA', f'background: {step_bg}')
        html_content = html_content.replace('background:#F8F9FA', f'background:{step_bg}')
        
        # Replace warning block backgrounds and borders
        html_content = html_content.replace('background: #FFF3CD', f'background: {warning_bg}')
        html_content = html_content.replace('background:#FFF3CD', f'background:{warning_bg}')
        html_content = html_content.replace('border: 1px solid #FFEAA7', f'border: 1px solid {warning_border}')
        html_content = html_content.replace('border:1px solid #FFEAA7', f'border:1px solid {warning_border}')
        
        # Replace code block backgrounds
        html_content = html_content.replace('background: #E8F0FE', f'background: {code_bg}')
        html_content = html_content.replace('background:#E8F0FE', f'background:{code_bg}')
        
        # Replace tab section backgrounds and borders
        html_content = html_content.replace('background: #FFF3CD', f'background: {tab_bg}')
        html_content = html_content.replace('border: 1px solid #FFEAA7', f'border: 1px solid {tab_border}')
        
        # Replace file info backgrounds
        html_content = html_content.replace('background: #F0F8FF', f'background: {file_bg}')
        html_content = html_content.replace('background:#F0F8FF', f'background:{file_bg}')
        
        # Replace important section backgrounds and borders
        html_content = html_content.replace('background: #FFEAA7', f'background: {important_bg}')
        html_content = html_content.replace('background:#FFEAA7', f'background:{important_bg}')
        html_content = html_content.replace('border-left: 4px solid #D4AC0D', f'border-left: 4px solid {important_border}')
        
        return html_content