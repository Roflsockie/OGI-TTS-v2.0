class LocalizationManager:
    """Manager for application localization"""

    def __init__(self):
        self.current_language = "English"
        self.translations = {
            "English": {
                "import_text": "Import Text",
                "play_text": "Play Text",
                "save_audio": "Save Audio",
                "open_folder": "Open Result",
                "copy_log": "Copy Log",
                "clear_log": "Clear Log",
                "download_models": "Download Models",
                "import_files": "Import Files",
                "convert": "Convert",
                "clear_list": "Clear List",
                "default_model": "Default Model:",
                "general_tab": "General",
                "text_to_audio_tab": "Text to Audio",
                "log_tab": "Log",
                "settings_tab": "Settings",
                "img_to_text_tab": "IMG to Text",
                "help_tab": "Help",
                "video_tutorial": "Video",
                "registration": "Registration",
                "imported_text_label": "Imported Text:",
                "app_log_label": "App Log:",
                "theme_label": "Theme:",
                "language_label": "Language:",
                "voice_settings_group": "Voice Settings",
                "speed_label": "Speed:",
                "volume_label": "Volume:",
                "pitch_label": "Pitch:",
                "translation_service_label": "Translation Service:",
                "api_key_label": "API Key:",
                "azure_endpoint_label": "Azure Endpoint:",
                "description_label": "Description:",
                "image_selection_group": "Image Selection",
                "ocr_service_label": "OCR Service:",
                "ocr_settings_group": "OCR Settings",
                "extract_text_button": "Extract Text from Image",
                "extracted_text_group": "Extracted Text",
                "save_text_button": "Save Text",
                "copy_text_button": "Copy Text",
                "select_guide_label": "Select guide:",
                "select_image": "Select Image",
                "microsoft_translator_desc": (
                    "Free tier: up to 50,000 characters per month.\n"
                    "To get a key, register on Azure Portal, create a Translator resource "
                    "and copy the key from the 'Keys and Endpoints' section.\n"
                    '<a href="https://portal.azure.com/" style="color: #0066CC;">Azure Portal</a> | '
                    '<a href="https://www.youtube.com/results?search_query=azure+translator+api+setup" style="color: #0066CC;">Video guide</a>\n'
                    "Enter the key in the field below."
                ),
                "google_translate_desc": (
                    "Free tier: up to 50,000 characters per month.\n"
                    "To get a key, create a project in Google Cloud Console, "
                    "enable Cloud Translation API, create credentials (API key).\n"
                    '<a href="https://console.cloud.google.com/" style="color: #0066CC;">Google Cloud Console</a> | '
                    '<a href="https://www.youtube.com/results?search_query=google+cloud+translate+api+setup" style="color: #0066CC;">Video guide</a>\n'
                    "Enter the key in the field below."
                ),
                "batch_import_tooltip": "Import multiple text files (.txt, .docx) and convert them to audio files. Each file will be processed separately with automatic language detection.",
                "support_author": "Support Author",
                "support_author_tooltip": "Support the developer",
                "translate_button": "Translate",
                "reset_settings_button": "Reset Settings",
                "reset_settings_tooltip": "Reset voice settings to default values (Speed: 100%, Volume: 100%, Pitch: 0Hz)"
            },
            "Русский": {
                "import_text": "Импорт текста",
                "play_text": "Воспроизвести",
                "save_audio": "Сохранить аудио",
                "open_folder": "Открыть результат",
                "copy_log": "Копировать лог",
                "clear_log": "Очистить лог",
                "download_models": "Скачать модели",
                "import_files": "Импорт файлов",
                "convert": "Конвертировать",
                "clear_list": "Очистить список",
                "default_model": "Модель по умолчанию:",
                "general_tab": "Основное",
                "text_to_audio_tab": "Текст в Аудио",
                "log_tab": "Лог",
                "settings_tab": "Настройки",
                "img_to_text_tab": "Изображение в Текст",
                "help_tab": "Справка",
                "video_tutorial": "Видео",
                "registration": "Регистрация",
                "imported_text_label": "Импортированный текст:",
                "app_log_label": "Лог приложения:",
                "theme_label": "Тема:",
                "language_label": "Язык:",
                "voice_settings_group": "Настройки голоса",
                "speed_label": "Скорость:",
                "volume_label": "Громкость:",
                "pitch_label": "Тон:",
                "translation_service_label": "Служба перевода:",
                "api_key_label": "API ключ:",
                "azure_endpoint_label": "Azure Endpoint:",
                "description_label": "Описание:",
                "image_selection_group": "Выбор изображения",
                "ocr_service_label": "OCR служба:",
                "ocr_settings_group": "Настройки OCR",
                "extract_text_button": "Извлечь текст из изображения",
                "extracted_text_group": "Извлеченный текст",
                "save_text_button": "Сохранить текст",
                "copy_text_button": "Копировать текст",
                "select_guide_label": "Выберите гайд:",
                "select_image": "Выбрать изображение",
                "microsoft_translator_desc": (
                    "Бесплатный уровень: до 50 000 символов в месяц.\n"
                    "Для получения ключа зарегистрируйтесь на Azure Portal, "
                    "создайте ресурс Translator и скопируйте ключ из раздела «Ключи и эндпоинты».\n"
                    '<a href="https://portal.azure.com/" style="color: #0066CC;">Azure Portal</a> | '
                    '<a href="https://www.youtube.com/results?search_query=azure+translator+api+setup" style="color: #0066CC;">Видео гайд</a>\n'
                    "Введите ключ в поле ниже."
                ),
                "google_translate_desc": (
                    "Бесплатный уровень: до 50 000 символов в месяц.\n"
                    "Для получения ключа создайте проект в Google Cloud Console, "
                    "включите API Cloud Translation, создайте учетные данные (API key).\n"
                    '<a href="https://console.cloud.google.com/" style="color: #0066CC;">Google Cloud Console</a> | '
                    '<a href="https://www.youtube.com/results?search_query=google+cloud+translate+api+setup" style="color: #0066CC;">Видео гайд</a>\n'
                    "Введите ключ в поле ниже."
                ),
                "batch_import_tooltip": "Импорт нескольких текстовых файлов (.txt, .docx) и конвертация их в аудиофайлы. Каждый файл будет обработан отдельно с автоматическим определением языка.",
                "support_author": "Поддержать автора",
                "support_author_tooltip": "Поддержать разработчика",
                "translate_button": "Перевести",
                "reset_settings_button": "Сброс настроек",
                "reset_settings_tooltip": "Сбросить настройки голоса к значениям по умолчанию (Скорость: 100%, Громкость: 100%, Тон: 0Hz)"
            },
            "Українська": {
                "import_text": "Імпорт тексту",
                "play_text": "Відтворити",
                "save_audio": "Зберегти аудіо",
                "open_folder": "Відкрити результат",
                "copy_log": "Копіювати лог",
                "clear_log": "Очистити лог",
                "download_models": "Завантажити моделі",
                "import_files": "Імпорт файлів",
                "convert": "Конвертувати",
                "clear_list": "Очистити список",
                "default_model": "Модель за замовчуванням:",
                "general_tab": "Основне",
                "text_to_audio_tab": "Текст в Аудіо",
                "log_tab": "Лог",
                "settings_tab": "Налаштування",
                "img_to_text_tab": "Зображення в Текст",
                "help_tab": "Довідка",
                "video_tutorial": "Відео",
                "registration": "Реєстрація",
                "imported_text_label": "Імпортований текст:",
                "app_log_label": "Лог додатку:",
                "theme_label": "Тема:",
                "language_label": "Мова:",
                "voice_settings_group": "Налаштування голосу",
                "speed_label": "Швидкість:",
                "volume_label": "Гучність:",
                "pitch_label": "Тон:",
                "translation_service_label": "Служба перекладу:",
                "api_key_label": "API ключ:",
                "azure_endpoint_label": "Azure Endpoint:",
                "description_label": "Опис:",
                "image_selection_group": "Вибір зображення",
                "ocr_service_label": "OCR служба:",
                "ocr_settings_group": "Налаштування OCR",
                "extract_text_button": "Видобути текст із зображення",
                "extracted_text_group": "Видобутий текст",
                "save_text_button": "Зберегти текст",
                "copy_text_button": "Копіювати текст",
                "select_guide_label": "Оберіть гайд:",
                "select_image": "Обрати зображення",
                "microsoft_translator_desc": (
                    "Безкоштовний рівень: до 50 000 символів на місяць.\n"
                    "Для отримання ключа зареєструйтеся на Azure Portal, "
                    "створіть ресурс Translator та скопіюйте ключ із розділу «Ключі та кінцеві точки».\n"
                    '<a href="https://portal.azure.com/" style="color: #0066CC;">Azure Portal</a> | '
                    '<a href="https://www.youtube.com/results?search_query=azure+translator+api+setup" style="color: #0066CC;">Відео гайд</a>\n'
                    "Введіть ключ у поле нижче."
                ),
                "google_translate_desc": (
                    "Безкоштовний рівень: до 50 000 символів на місяць.\n"
                    "Для отримання ключа створіть проект у Google Cloud Console, "
                    "увімкніть API Cloud Translation, створіть облікові дані (API key).\n"
                    '<a href="https://console.cloud.google.com/" style="color: #0066CC;">Google Cloud Console</a> | '
                    '<a href="https://www.youtube.com/results?search_query=google+cloud+translate+api+setup" style="color: #0066CC;">Відео гайд</a>\n'
                    "Введіть ключ у поле нижче."
                ),
                "batch_import_tooltip": "Імпорт декількох текстових файлів (.txt, .docx) та конвертація їх в аудіофайли. Кожен файл буде оброблено окремо з автоматичним визначенням мови.",
                "support_author": "Підтримати автора",
                "support_author_tooltip": "Підтримати розробника",
                "translate_button": "Перекласти",
                "reset_settings_button": "Скинути налаштування",
                "reset_settings_tooltip": "Скинути налаштування голосу до значень за замовчуванням (Швидкість: 100%, Гучність: 100%, Тон: 0Hz)"
            }
        }

    def set_language(self, language):
        """Set current language"""
        if language in self.translations:
            self.current_language = language
            return True
        return False

    def get_text(self, key):
        """Get translated text for current language"""
        return self.translations.get(self.current_language, self.translations["English"]).get(key, key)

    def apply_localization(self, main_window, language):
        """Apply localization to main window UI elements"""
        # Set the language first
        self.set_language(language)
        # Update button texts
        if hasattr(main_window, 'pushButton') and main_window.pushButton is not None:
            main_window.pushButton.setText(self.get_text("import_text"))
        if hasattr(main_window, 'pushButton_2') and main_window.pushButton_2 is not None:
            main_window.pushButton_2.setText(self.get_text("play_text"))
        if hasattr(main_window, 'pushButton_3') and main_window.pushButton_3 is not None:
            main_window.pushButton_3.setText(self.get_text("save_audio"))
        if hasattr(main_window, 'pushButton_4') and main_window.pushButton_4 is not None:
            main_window.pushButton_4.setText(self.get_text("open_folder"))
        if hasattr(main_window, 'pushButton_7') and main_window.pushButton_7 is not None:
            main_window.pushButton_7.setText(self.get_text("open_folder"))
        if hasattr(main_window, 'pushButton_5') and main_window.pushButton_5 is not None:
            main_window.pushButton_5.setText(self.get_text("copy_log"))
        if hasattr(main_window, 'pushButton_6') and main_window.pushButton_6 is not None:
            main_window.pushButton_6.setText(self.get_text("clear_log"))
        if hasattr(main_window, 'custom_models_button') and main_window.custom_models_button is not None:
            main_window.custom_models_button.setText(self.get_text("download_models"))

        # Support button
        if hasattr(main_window, 'supportButton') and main_window.supportButton is not None:
            main_window.supportButton.setText(self.get_text("support_author"))
            main_window.supportButton.setToolTip(self.get_text("support_author_tooltip"))

        # Reset settings button
        if hasattr(main_window, 'resetVoiceSettingsButton') and main_window.resetVoiceSettingsButton is not None:
            main_window.resetVoiceSettingsButton.setText(self.get_text("reset_settings_button"))
            main_window.resetVoiceSettingsButton.setToolTip(self.get_text("reset_settings_tooltip"))

        # Batch processing buttons
        if hasattr(main_window, 'batchImportButton') and main_window.batchImportButton is not None:
            main_window.batchImportButton.setText(self.get_text("import_files"))
        if hasattr(main_window, 'batchProcessButton') and main_window.batchProcessButton is not None:
            main_window.batchProcessButton.setText(self.get_text("convert"))
        if hasattr(main_window, 'clearBatchListButton') and main_window.clearBatchListButton is not None:
            main_window.clearBatchListButton.setText(self.get_text("clear_list"))
        if hasattr(main_window, 'batchModelLabel') and main_window.batchModelLabel is not None:
            main_window.batchModelLabel.setText(self.get_text("default_model"))
        if hasattr(main_window, 'batchInfoLabel') and main_window.batchInfoLabel is not None:
            main_window.batchInfoLabel.setText(self.get_text("batch_import_tooltip"))

        # Translator buttons
        if hasattr(main_window, 'translatorRegisterButton') and main_window.translatorRegisterButton is not None:
            main_window.translatorRegisterButton.setText(self.get_text("registration"))
        if hasattr(main_window, 'translateButton') and main_window.translateButton is not None:
            main_window.translateButton.setText(self.get_text("translate_button"))

        # IMG to Text buttons
        if hasattr(main_window, 'selectImageButton') and main_window.selectImageButton is not None:
            main_window.selectImageButton.setText(self.get_text("select_image"))
        if hasattr(main_window, 'extractTextButton') and main_window.extractTextButton is not None:
            main_window.extractTextButton.setText(self.get_text("extract_text_button"))
        if hasattr(main_window, 'saveExtractedTextButton') and main_window.saveExtractedTextButton is not None:
            main_window.saveExtractedTextButton.setText(self.get_text("save_text_button"))
        if hasattr(main_window, 'copyExtractedTextButton') and main_window.copyExtractedTextButton is not None:
            main_window.copyExtractedTextButton.setText(self.get_text("copy_text_button"))

        # Labels
        if hasattr(main_window, 'label_4') and main_window.label_4 is not None:
            main_window.label_4.setText(self.get_text("imported_text_label"))
        if hasattr(main_window, 'label_5') and main_window.label_5 is not None:
            main_window.label_5.setText(self.get_text("app_log_label"))
        if hasattr(main_window, 'label_6') and main_window.label_6 is not None:
            main_window.label_6.setText(self.get_text("theme_label"))
        if hasattr(main_window, 'languageLabel') and main_window.languageLabel is not None:
            main_window.languageLabel.setText(self.get_text("language_label"))
        if hasattr(main_window, 'speedLabel') and main_window.speedLabel is not None:
            main_window.speedLabel.setText(self.get_text("speed_label"))
        if hasattr(main_window, 'volumeLabel') and main_window.volumeLabel is not None:
            main_window.volumeLabel.setText(self.get_text("volume_label"))
        if hasattr(main_window, 'pitchLabel') and main_window.pitchLabel is not None:
            main_window.pitchLabel.setText(self.get_text("pitch_label"))
        if hasattr(main_window, 'translatorServiceLabel') and main_window.translatorServiceLabel is not None:
            main_window.translatorServiceLabel.setText(self.get_text("translation_service_label"))
        if hasattr(main_window, 'translatorApiLabel') and main_window.translatorApiLabel is not None:
            main_window.translatorApiLabel.setText(self.get_text("api_key_label"))
        if hasattr(main_window, 'translatorDescriptionLabel') and main_window.translatorDescriptionLabel is not None:
            main_window.translatorDescriptionLabel.setText(self.get_text("description_label"))
        if hasattr(main_window, 'ocrServiceLabel') and main_window.ocrServiceLabel is not None:
            main_window.ocrServiceLabel.setText(self.get_text("ocr_service_label"))
        if hasattr(main_window, 'ocrApiKeyLabel') and main_window.ocrApiKeyLabel is not None:
            main_window.ocrApiKeyLabel.setText(self.get_text("api_key_label"))
        if hasattr(main_window, 'azureEndpointLabel') and main_window.azureEndpointLabel is not None:
            main_window.azureEndpointLabel.setText(self.get_text("azure_endpoint_label"))
        if hasattr(main_window, 'helpGuideLabel') and main_window.helpGuideLabel is not None:
            main_window.helpGuideLabel.setText(self.get_text("select_guide_label"))

        # Group boxes
        if hasattr(main_window, 'voiceSettingsGroup') and main_window.voiceSettingsGroup is not None:
            main_window.voiceSettingsGroup.setTitle(self.get_text("voice_settings_group"))
        if hasattr(main_window, 'imageSelectionGroup') and main_window.imageSelectionGroup is not None:
            main_window.imageSelectionGroup.setTitle(self.get_text("image_selection_group"))
        if hasattr(main_window, 'ocrSettingsGroup') and main_window.ocrSettingsGroup is not None:
            main_window.ocrSettingsGroup.setTitle(self.get_text("ocr_settings_group"))
        if hasattr(main_window, 'extractedTextGroup') and main_window.extractedTextGroup is not None:
            main_window.extractedTextGroup.setTitle(self.get_text("extracted_text_group"))

        # Tab names
        if hasattr(main_window, 'tabWidget') and main_window.tabWidget is not None:
            main_window.tabWidget.setTabText(0, self.get_text("general_tab"))
            main_window.tabWidget.setTabText(1, self.get_text("text_to_audio_tab"))
            main_window.tabWidget.setTabText(2, self.get_text("log_tab"))
            main_window.tabWidget.setTabText(3, self.get_text("settings_tab"))
            main_window.tabWidget.setTabText(4, self.get_text("img_to_text_tab"))
            main_window.tabWidget.setTabText(5, self.get_text("help_tab"))

        # Update translator description if settings tab manager exists
        if hasattr(main_window, 'settings_tab_manager') and hasattr(main_window.settings_tab_manager, 'update_translator_description'):
            if hasattr(main_window, 'translatorServiceComboBox'):
                current_service = main_window.translatorServiceComboBox.currentText()
                main_window.settings_tab_manager.update_translator_description(current_service)