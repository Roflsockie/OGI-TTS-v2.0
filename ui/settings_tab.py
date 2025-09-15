import os
import sys
import shutil
import webbrowser
from core.settings import load_settings, save_settings
from core.translator import TranslatorManager, TranslatorError
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox

class SettingsTabManager:
    """Manager for Settings tab functionality"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.translator_manager = TranslatorManager()
        self.setup_translator_ui()

    def setup_settings_combo_boxes(self):
        """Setup combo boxes in Settings tab"""
        try:
            # Theme/Style combo box - now contains styles instead of themes
            self.main_window.themeComboBox.addItems(["Light", "Dark"])
            self.main_window.themeComboBox.setCurrentText("Dark")
            self.main_window.themeComboBox.currentTextChanged.connect(self.change_style)

            # Language combo box for interface localization
            self.main_window.languageComboBox.addItems(["English", "Русский", "Українська"])
            self.main_window.languageComboBox.setCurrentText("English")
            self.main_window.languageComboBox.currentTextChanged.connect(self.change_language)
        except AttributeError as e:
            print(f"Settings combo box error: {e}")

    def load_saved_settings(self):
        """Load and apply saved settings"""
        settings = load_settings()

        # Load saved style
        saved_style = settings.get('selected_style', 'Dark')
        if saved_style in ["Light", "Dark"]:
            self.main_window.themeComboBox.setCurrentText(saved_style)
            # The change_style function will be called automatically due to the signal connection

        # Load saved language
        saved_language = settings.get('selected_language', 'English')
        if saved_language in ["English", "Русский", "Українська"]:
            self.main_window.languageComboBox.setCurrentText(saved_language)
            # The change_language function will be called automatically due to the signal connection

        # Load translator settings
        self.load_translator_settings()

    def change_style(self):
        """Change style based on combo box selection"""
        style = self.main_window.themeComboBox.currentText()
        self.main_window.log_message(f"Applying style: {style}", "pink")

        try:
            if style == "Light":
                # Apply custom CSS for larger fonts like in OgiDark theme
                default_css = """
                QTextEdit {
                    font: 11pt "Segoe UI";
                }
                QLabel {
                    font: 10pt "Segoe UI";
                }
                QGroupBox {
                    font: 11pt "Segoe UI";
                }
                """
                self.main_window.setStyleSheet(default_css)
                self.main_window.log_message("Applied light style with larger fonts", "green")
            elif style == "Dark":
                # Map style names to file names
                style_files = {
                    "Dark": "ogidark.css"
                }
                style_file = style_files.get(style, "ogidark.css")
                style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles', style_file)
                if os.path.exists(style_path):
                    with open(style_path, 'r', encoding='utf-8') as f:
                        stylesheet = f.read()
                    self.main_window.setStyleSheet(stylesheet)
                    self.main_window.log_message(f"Applied {style} style successfully", "green")
                else:
                    self.main_window.log_message(f"Style file {style_file} not found", "red")
            else:
                style_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles', f'{style}.qss')
                if os.path.exists(style_file):
                    with open(style_file, 'r', encoding='utf-8') as f:
                        stylesheet = f.read()
                    self.main_window.setStyleSheet(stylesheet)
                    self.main_window.log_message(f"Applied {style} style successfully", "green")
                else:
                    self.main_window.log_message(f"Style file {style}.qss not found", "red")

            # Save the selected style
            settings = load_settings()
            settings['selected_style'] = style
            save_settings(settings)

        except Exception as e:
            self.main_window.log_message(f"Error applying style {style}: {e}", "red")

    def change_language(self):
        """Change interface language based on combo box selection"""
        language = self.main_window.languageComboBox.currentText()
        self.main_window.log_message(f"Changing interface language to: {language}", "pink")

        try:
            # Save the selected language
            settings = load_settings()
            settings['selected_language'] = language
            save_settings(settings)

            # Apply language changes to UI elements
            self.main_window.localization_manager.set_language(language)
            self.main_window.localization_manager.apply_localization(self.main_window)

            # Update translator description with new language
            if hasattr(self.main_window, 'translatorServiceComboBox'):
                current_service = self.main_window.translatorServiceComboBox.currentText()
                self.update_translator_description(current_service)

            self.main_window.log_message(f"Interface language changed to {language}", "green")

        except Exception as e:
            self.main_window.log_message(f"Error changing language to {language}: {e}", "red")

    def setup_translator_ui(self):
        """Setup translator UI elements from Qt Designer"""
        try:
            # Connect signals for translator elements
            if hasattr(self.main_window, 'translatorServiceComboBox'):
                self.main_window.translatorServiceComboBox.addItems(["Microsoft Translator", "Google Cloud Translate"])
                self.main_window.translatorServiceComboBox.currentTextChanged.connect(self.update_translator_description)
                self.main_window.translatorServiceComboBox.currentTextChanged.connect(self.save_translator_settings)
                self.main_window.translatorServiceComboBox.currentTextChanged.connect(self.update_translator_api_key_status)

            if hasattr(self.main_window, 'translatorApiKeyInput'):
                self.main_window.translatorApiKeyInput.textChanged.connect(self.save_translator_settings)
                self.main_window.translatorApiKeyInput.textChanged.connect(self.update_translator_api_key_status)

            if hasattr(self.main_window, 'translatorVideoButton'):
                self.main_window.translatorVideoButton.clicked.connect(self.open_video_tutorial)

            if hasattr(self.main_window, 'translatorRegisterButton'):
                self.main_window.translatorRegisterButton.clicked.connect(self.open_registration_page)

            # Load saved settings and update description
            self.load_translator_settings()
            if hasattr(self.main_window, 'translatorServiceComboBox'):
                self.update_translator_description(self.main_window.translatorServiceComboBox.currentText())

        except Exception as e:
            print(f"Translator UI setup error: {e}")

    def update_translator_description(self, service_name):
        """Update description based on selected service"""
        descriptions = self.translator_manager.get_service_descriptions(self.main_window.localization_manager)
        description = descriptions.get(service_name, "")
        if hasattr(self.main_window, 'translatorDescriptionText'):
            self.main_window.translatorDescriptionText.setHtml(description)

    def update_translator_api_key_status(self):
        """Update translator API key status icon based on current input and service"""
        if not hasattr(self.main_window, 'translatorApiKeyStatusLabel') or not hasattr(self.main_window, 'translatorApiKeyInput'):
            return

        api_key = self.main_window.translatorApiKeyInput.text().strip()
        service = self.main_window.translatorServiceComboBox.currentText() if hasattr(self.main_window, 'translatorServiceComboBox') else "Microsoft Translator"

        # Default status: empty field
        if not api_key:
            self.main_window.translatorApiKeyStatusLabel.setText("⭕")
            self.main_window.translatorApiKeyStatusLabel.setToolTip("API Key Status: No key entered")
            return

        # Test the key asynchronously (don't block UI)
        try:
            translator = self.translator_manager.get_translator(service, api_key)
            if translator.test_key():
                self.main_window.translatorApiKeyStatusLabel.setText("✅")
                self.main_window.translatorApiKeyStatusLabel.setToolTip("API Key Status: Valid")
            else:
                self.main_window.translatorApiKeyStatusLabel.setText("❌")
                self.main_window.translatorApiKeyStatusLabel.setToolTip("API Key Status: Invalid")

        except Exception as e:
            # On error, show neutral status
            self.main_window.translatorApiKeyStatusLabel.setText("⭕")
            self.main_window.translatorApiKeyStatusLabel.setToolTip(f"API Key Status: Error - {str(e)}")

    def test_translator_api_key(self):
        """Test the translator API key (legacy method, kept for compatibility)"""
        if not hasattr(self.main_window, 'translatorServiceComboBox') or not hasattr(self.main_window, 'translatorApiKeyInput'):
            QMessageBox.warning(self.main_window, "UI Error", "Translator UI elements not found.")
            return

        service = self.main_window.translatorServiceComboBox.currentText()
        api_key = self.main_window.translatorApiKeyInput.text().strip()

        if not api_key:
            QMessageBox.warning(self.main_window, "API Key Required",
                              "Please enter an API key first.")
            return

        try:
            translator = self.translator_manager.get_translator(service, api_key)
            if translator.test_key():
                QMessageBox.information(self.main_window, "API Key Valid",
                                      "API key is valid and working!")
                self.main_window.log_message("Translator API key tested successfully", "green")
            else:
                QMessageBox.warning(self.main_window, "API Key Invalid",
                                  "API key is invalid or service is unavailable.")
                self.main_window.log_message("Translator API key test failed", "red")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Test Failed",
                               f"Error testing API key: {str(e)}")
            self.main_window.log_message(f"Translator API key test error: {e}", "red")

    def load_translator_settings(self):
        """Load translator settings"""
        settings = load_settings()
        service = settings.get('translator_service', 'Microsoft Translator')
        api_key = settings.get('translator_api_key', '')

        if hasattr(self.main_window, 'translatorServiceComboBox'):
            self.main_window.translatorServiceComboBox.setCurrentText(service)
        if hasattr(self.main_window, 'translatorApiKeyInput'):
            self.main_window.translatorApiKeyInput.setText(api_key)

    def save_translator_settings(self):
        """Save translator settings"""
        settings = load_settings()
        if hasattr(self.main_window, 'translatorServiceComboBox'):
            settings['translator_service'] = self.main_window.translatorServiceComboBox.currentText()
        if hasattr(self.main_window, 'translatorApiKeyInput'):
            settings['translator_api_key'] = self.main_window.translatorApiKeyInput.text()
        save_settings(settings)

    def open_video_tutorial(self):
        """Open video tutorial for selected service"""
        if not hasattr(self.main_window, 'translatorServiceComboBox'):
            return

        service = self.main_window.translatorServiceComboBox.currentText()
        video_urls = {
            "Microsoft Translator": "https://www.youtube.com/results?search_query=azure+translator+api+setup",
            "Google Cloud Translate": "https://www.youtube.com/results?search_query=google+cloud+translate+api+setup"
        }

        url = video_urls.get(service)
        if url:
            webbrowser.open(url)
            self.main_window.log_message(f"Opened video tutorial for {service}", "pink")
        else:
            self.main_window.log_message("Video tutorial URL not found", "red")

    def open_registration_page(self):
        """Open registration page for selected service"""
        if not hasattr(self.main_window, 'translatorServiceComboBox'):
            return

        service = self.main_window.translatorServiceComboBox.currentText()
        registration_urls = {
            "Microsoft Translator": "https://portal.azure.com/",
            "Google Cloud Translate": "https://console.cloud.google.com/"
        }

        url = registration_urls.get(service)
        if url:
            webbrowser.open(url)
            self.main_window.log_message(f"Opened registration page for {service}", "pink")
        else:
            self.main_window.log_message("Registration URL not found", "red")