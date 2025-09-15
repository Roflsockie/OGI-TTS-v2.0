import os
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from langdetect import detect
from docx import Document
from core.tts_worker import TTSWorker
from core.settings import load_settings, save_settings
from core.translator import TranslatorManager, TranslatorError

class GeneralTabManager:
    """Manager for General tab functionality"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.selected_file = None
        self.text_content = ""
        self.translated_text = None  # Store translated text separately
        self.translator_manager = TranslatorManager()

    def import_text(self):
        """Import text from file"""
        program_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Select Text File", program_dir, "Text Files (*.txt *.docx)")
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.text_content = f.read()
                elif file_path.endswith('.docx'):
                    doc = Document(file_path)
                    self.text_content = '\n'.join([para.text for para in doc.paragraphs])

                char_count = len(self.text_content)
                # Set text in the text edit widget
                if hasattr(self.main_window, 'text_edit'):
                    self.main_window.text_edit.setPlainText(self.text_content)
                self.translated_text = None  # Reset translated text on new import
                self.main_window.log_message(f"File: {filename}", "green")
                self.main_window.log_message(f"Characters: {char_count}", "green")
                # Detect language
                try:
                    detected_lang = detect(self.text_content)
                    if detected_lang == 'ru':
                        self.main_window.comboBox_2.setCurrentText("Russian")
                    elif detected_lang == 'en':
                        self.main_window.comboBox_2.setCurrentText("English")
                    elif detected_lang == 'uk':
                        self.main_window.comboBox_2.setCurrentText("Ukrainian")
                    elif detected_lang == 'ja':
                        self.main_window.comboBox_2.setCurrentText("Japanese")
                    else:
                        self.main_window.comboBox_2.setCurrentText("English")
                    self.main_window.log_message(f"Detected language: {self.main_window.comboBox_2.currentText()}", "green")
                except:
                    self.main_window.comboBox_2.setCurrentText("English")
                    self.main_window.log_message("Language detection failed, defaulting to English", "yellow")
            except Exception as e:
                self.main_window.log_message(f"Error importing file: {e}", "red")

    def play_selected(self):
        """Play selected text from text edit"""
        if not hasattr(self.main_window, 'text_edit') or not self.main_window.text_edit:
            self.main_window.log_message("Text editor not available", "red")
            return

        # Get selected text
        cursor = self.main_window.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        if not selected_text:
            self.main_window.log_message("No text selected. Select text and try again.", "orange")
            return

        if len(selected_text) < 10:
            self.main_window.log_message("Selected text too short (minimum 10 characters)", "orange")
            return

        voice = self.get_selected_voice()
        model = self.main_window.comboBox.currentText()

        self.main_window.log_message(f"Playing selected text ({len(selected_text)} chars)", "blue")

        self.main_window.worker = TTSWorker(selected_text, voice, None,
                               speed=self.main_window.voice_speed,
                               volume=self.main_window.voice_volume,
                               pitch=self.main_window.voice_pitch,
                               play_only=True, model=model)
        self.main_window.worker.progress.connect(self.main_window.update_progress)
        self.main_window.worker.log_signal.connect(lambda msg: self.main_window.log_message(msg, "blue"))
        self.main_window.worker.finished.connect(self.main_window.on_tts_finished)
        self.main_window.show_progress_bar()
        self.main_window.worker.start()

    def save_to_audio(self):
        """Save text content to audio file"""
        if not self.text_content:
            self.main_window.log_message("Import text first", "red")
            return
        voice = self.get_selected_voice()
        model = self.main_window.comboBox.currentText()

        # Create output directory - use correct base directory for portable version
        if getattr(sys, 'frozen', False):
            # Running as packaged exe - use exe directory
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running in development - find project root (directory containing main.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up until we find main.py or reach drive root
            while current_dir and current_dir != os.path.dirname(current_dir):
                if os.path.exists(os.path.join(current_dir, 'main.py')):
                    base_dir = current_dir
                    break
                current_dir = os.path.dirname(current_dir)
            else:
                # Fallback to script directory if main.py not found
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        output_dir = os.path.join(base_dir, 'tts_audio')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.main_window.log_message(f"Created folder: <b>{output_dir}</b>", "white")
        output_file = os.path.join(output_dir, self.generate_filename(is_example=False))

        self.main_window.worker = TTSWorker(self.text_content, voice, output_file,
                               speed=self.main_window.voice_speed,
                               volume=self.main_window.voice_volume,
                               pitch=self.main_window.voice_pitch,
                               model=model)
        self.main_window.worker.progress.connect(self.main_window.update_progress)
        self.main_window.worker.log_signal.connect(lambda msg: self.main_window.log_message(msg, "blue"))
        self.main_window.worker.finished.connect(self.main_window.on_tts_finished)
        self.main_window.show_progress_bar()
        self.main_window.worker.start()

    def get_selected_voice(self):
        """Get selected voice based on current combo box selections"""
        model = self.main_window.comboBox.currentText()
        language = self.main_window.comboBox_2.currentText()
        voice_type = self.main_window.comboBox_3.currentText()
        if model == "Edge TTS":
            voice_map = {
                "English": {"Male": "en-US-ZiraNeural", "Female": "en-US-AriaNeural"},
                "Russian": {"Male": "ru-RU-DmitryNeural", "Female": "ru-RU-SvetlanaNeural"},
                "Ukrainian": {"Male": "uk-UA-OstapNeural", "Female": "uk-UA-PolinaNeural"},
                "Japanese": {"Male": "ja-JP-KeitaNeural", "Female": "ja-JP-NanamiNeural"}
            }
            return voice_map.get(language, {}).get(voice_type, "en-US-AriaNeural")
        return "en-US-AriaNeural"

    def generate_filename(self, is_example=False):
        """Generate filename for audio output"""
        model = self.main_window.comboBox.currentText()
        language = self.main_window.comboBox_2.currentText()
        voice_type = self.main_window.comboBox_3.currentText()
        lang_code = {
            "Russian": "ru",
            "English": "eng",
            "Ukrainian": "ua",
            "Japanese": "jp"
        }.get(language, "unk")

        if model == "Edge TTS":
            voice_short = {
                "en-US-ZiraNeural": "zira",
                "en-US-AriaNeural": "aria",
                "ru-RU-DmitryNeural": "dmitry",
                "ru-RU-SvetlanaNeural": "svetlana",
                "uk-UA-OstapNeural": "ostap",
                "uk-UA-PolinaNeural": "polina",
                "ja-JP-KeitaNeural": "keita",
                "ja-JP-NanamiNeural": "nanami"
            }
            voice_tag = voice_short.get(self.get_selected_voice(), voice_type.lower()[:3])
            model_tag = "edge"

        if is_example:
            return f"example_{model_tag}{voice_tag}_{lang_code}.wav"
        else:
            return f"{lang_code}_output_{model_tag}{voice_tag}.wav"

    def update_voice_options(self):
        """Update voice options based on selected language and model"""
        model = self.main_window.comboBox.currentText()
        language = self.main_window.comboBox_2.currentText()
        self.main_window.comboBox_3.clear()
        if model == "Edge TTS":
            if language == "English":
                self.main_window.comboBox_3.addItems(["Male", "Female"])
            elif language == "Russian":
                self.main_window.comboBox_3.addItems(["Male", "Female"])
            elif language == "Ukrainian":
                self.main_window.comboBox_3.addItems(["Male", "Female"])
            elif language == "Japanese":
                self.main_window.comboBox_3.addItems(["Male", "Female"])
        self.main_window.comboBox_3.setCurrentText("Female")

    def translate_text(self):
        """Translate text using selected translator service"""
        if not self.text_content:
            self.main_window.log_message("Import text first", "red")
            return

        # Get translator settings
        settings = load_settings()
        service = settings.get('translator_service', 'Microsoft Translator')
        api_key = settings.get('translator_api_key', '')

        if not api_key:
            QMessageBox.warning(self.main_window, "API Key Required",
                              "Please set up translator API key in Settings first.")
            return

        # Get target language from combo box (assuming we add one)
        target_lang = getattr(self.main_window, 'translateLangComboBox', None)
        if target_lang:
            target_language = target_lang.currentText()
        else:
            target_language = "English"

        self.main_window.log_message(f"Translating text to {target_language} using {service}...", "blue")

        try:
            translator = self.translator_manager.get_translator(service, api_key)
            translated_text = translator.translate(self.text_content, target_language)

            # Update text content and UI
            self.text_content = translated_text
            self.translated_text = translated_text
            if hasattr(self.main_window, 'text_edit'):
                self.main_window.text_edit.setPlainText(translated_text)

            # Auto-detect language of translated text and update UI
            try:
                detected_lang = detect(translated_text)
                if detected_lang == 'ru':
                    self.main_window.comboBox_2.setCurrentText("Russian")
                elif detected_lang == 'en':
                    self.main_window.comboBox_2.setCurrentText("English")
                elif detected_lang == 'uk':
                    self.main_window.comboBox_2.setCurrentText("Ukrainian")
                elif detected_lang == 'ja':
                    self.main_window.comboBox_2.setCurrentText("Japanese")
                else:
                    self.main_window.comboBox_2.setCurrentText("English")
                # Update voice options for the detected language
                self.update_voice_options()
                self.main_window.log_message(f"Detected translated language: {self.main_window.comboBox_2.currentText()}", "green")
            except:
                self.main_window.log_message("Language detection for translated text failed", "yellow")

            self.main_window.log_message(f"Text translated successfully ({len(translated_text)} chars)", "green")

        except TranslatorError as e:
            QMessageBox.critical(self.main_window, "Translation Error", str(e))
            self.main_window.log_message(f"Translation failed: {e}", "red")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Translation Error", f"Unexpected error: {str(e)}")
            self.main_window.log_message(f"Translation error: {e}", "red")