import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPlainTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel, QSlider, QSpinBox, QHBoxLayout, QGroupBox, QStyle, QListWidget, QProgressBar, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
import webbrowser

# Import modular components
from core.tts_worker import TTSWorker
from core.settings import load_settings, save_settings
from core.localization import LocalizationManager
from core.title_bar import set_title_bar_color, get_hwnd_from_widget
from ui.general_tab import GeneralTabManager
from ui.batch_tab import BatchTabManager
from ui.settings_tab import SettingsTabManager
from ui.img_to_text_tab import ImgToTextTabManager
from ui.help_tab import HelpTabManager

# Disable Qt warnings
os.environ['QT_LOGGING_RULES'] = '*.warning=false'

# Disable CSS stylesheet warnings
import logging
logging.getLogger('PyQt5.QtCore').setLevel(logging.ERROR)

# Global exception handler to keep terminal open
def exception_hook(exctype, value, traceback):
    print(f"Uncaught exception: {exctype} {value}")
    print("Traceback:")
    import traceback as tb
    tb.print_tb(traceback)
    input("Press Enter to exit...")

sys.excepthook = exception_hook

# FFMPEG is optional - edge-tts will use system FFMPEG if available
print("OGI TTS v2.0 starting...")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        uic.loadUi(ui_path, self)

        # Enable external links for translator description text (if supported)
        if hasattr(self, 'translatorDescriptionText') and hasattr(self.translatorDescriptionText, 'setOpenExternalLinks'):
            self.translatorDescriptionText.setOpenExternalLinks(True)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), 'logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Set window title
        self.setWindowTitle("OGI TTS V2.0")

        # Variables
        self.selected_file = None
        self.text_content = ""
        
        # Voice settings variables
        self.voice_speed = 1.0  # 0.5x to 2.0x
        self.voice_volume = 100  # 0 to 100
        self.voice_pitch = 0  # -50 to +50 Hz

        # Batch processing variables
        self.batch_files = []  # List of (file_path, content, detected_lang, selected_model, selected_lang, selected_voice)
        self.batch_processing = False

        # Create text widgets (exactly as in your Qt Designer layout)
        self.create_text_widgets()

        # Create voice settings UI - moved before setup_combo_boxes
        self.create_voice_settings_ui()

        # Load saved settings again to ensure voice UI is properly initialized
        self.load_saved_settings()

        # Initialize localization manager
        self.localization_manager = LocalizationManager()

        # Initialize tab managers
        self.general_tab_manager = GeneralTabManager(self)
        self.batch_tab_manager = BatchTabManager(self)
        self.settings_tab_manager = SettingsTabManager(self)
        self.img_to_text_tab_manager = ImgToTextTabManager(self)
        self.help_tab_manager = HelpTabManager(self)

        # Setup UI for tab managers
        self.img_to_text_tab_manager.setup_ui()
        self.help_tab_manager.setup_ui()

        # Set default tab to General
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setCurrentIndex(0)

        # Setup combo boxes
        self.setup_combo_boxes()

        # Connect buttons
        self.connect_buttons()

        # Set window properties
        self.setMinimumSize(680, 500)

        # Set window flags for better title bar appearance
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)

    def showEvent(self, event):
        """Handle window show event to apply theme after UI is fully initialized"""
        super().showEvent(event)

        # Apply the current theme after window is shown to ensure proper rendering
        current_style = self.themeComboBox.currentText() if hasattr(self, 'themeComboBox') else "Dark"
        if current_style == "Dark":
            self.change_style()
        elif current_style == "Light":
            self.change_style()

        # Apply initial language localization after window is shown
        initial_language = load_settings().get('selected_language', 'English')
        self.apply_language_localization(initial_language)

    def resizeEvent(self, event):
        """Handle window resize to adjust tabWidget and other elements"""
        super().resizeEvent(event)

        # Get current window size
        window_size = self.size()

        # Adjust tabWidget to fill most of the window (leave space for button and progress bar)
        if hasattr(self, 'tabWidget'):
            tab_height = window_size.height() - 80  # Leave space for button (27) + progress bar (20) + margins
            self.tabWidget.setGeometry(0, 0, window_size.width(), tab_height)

        # NOTE: Open Result button stays in its tab (General tab) - don't move it to main window level

        # Adjust progress bar position and width
        if hasattr(self, 'batchProgressBar'):
            progress_y = window_size.height() - 45  # Position progress bar at bottom
            progress_width = window_size.width() - 20  # Full width minus margins
            self.batchProgressBar.setGeometry(10, progress_y, progress_width, 20)

        event.accept()

        # Temporarily disabled - no default theme applied
        # self.apply_dark_theme()

        # Voice settings UI already created above

    def create_voice_settings_ui(self):
        """Find and setup voice settings UI elements from Qt Designer"""
        # Find voice settings group
        self.voice_group = self.findChild(QGroupBox, "voiceSettingsGroup")

        # Find sliders
        self.speed_slider = self.findChild(QSlider, "speedSlider")
        self.volume_slider = self.findChild(QSlider, "volumeSlider")
        self.pitch_slider = self.findChild(QSlider, "pitchSlider")

        # Find spin boxes
        self.speed_spinbox = self.findChild(QSpinBox, "speedSpinBox")
        self.volume_spinbox = self.findChild(QSpinBox, "volumeSpinBox")
        self.pitch_spinbox = self.findChild(QSpinBox, "pitchSpinBox")

        # Find warning label
        self.voice_warning_label = self.findChild(QLabel, "voiceWarningLabel")

        # Connect slider and spinbox signals if elements exist
        if self.speed_slider and self.speed_spinbox:
            self.speed_slider.valueChanged.connect(self.speed_spinbox.setValue)
            self.speed_spinbox.valueChanged.connect(self.speed_slider.setValue)
            self.speed_slider.sliderReleased.connect(lambda: self.update_voice_speed(self.speed_slider.value()))

        if self.volume_slider and self.volume_spinbox:
            self.volume_slider.valueChanged.connect(self.volume_spinbox.setValue)
            self.volume_spinbox.valueChanged.connect(self.volume_slider.setValue)
            self.volume_slider.sliderReleased.connect(lambda: self.update_voice_volume(self.volume_slider.value()))

        if self.pitch_slider and self.pitch_spinbox:
            self.pitch_slider.valueChanged.connect(self.pitch_spinbox.setValue)
            self.pitch_spinbox.valueChanged.connect(self.pitch_slider.setValue)
            self.pitch_slider.sliderReleased.connect(lambda: self.update_voice_pitch(self.pitch_slider.value()))

    def update_voice_speed(self, value):
        """Update voice speed setting"""
        self.voice_speed = value / 100.0  # Convert percentage to multiplier
        self.log_message(f"Voice speed set to {self.voice_speed:.1f}x", "blue")
        self.save_voice_settings()

    def update_voice_volume(self, value):
        """Update voice volume setting"""
        self.voice_volume = value
        self.log_message(f"Voice volume set to {self.voice_volume}%", "blue")
        self.save_voice_settings()

    def update_voice_pitch(self, value):
        """Update voice pitch setting"""
        self.voice_pitch = value
        self.log_message(f"Voice pitch set to {self.voice_pitch}Hz", "blue")
        self.save_voice_settings()

    def reset_voice_settings(self):
        """Reset voice settings to default values"""
        try:
            # Set default values
            default_speed = 100  # 100%
            default_volume = 100  # 100%
            default_pitch = 0  # 0Hz

            # Update internal variables
            self.voice_speed = default_speed / 100.0  # Convert to multiplier
            self.voice_volume = default_volume
            self.voice_pitch = default_pitch

            # Update UI elements if they exist
            if hasattr(self, 'speed_slider') and self.speed_slider:
                self.speed_slider.setValue(default_speed)
            if hasattr(self, 'volume_slider') and self.volume_slider:
                self.volume_slider.setValue(default_volume)
            if hasattr(self, 'pitch_slider') and self.pitch_slider:
                self.pitch_slider.setValue(default_pitch)

            # Save settings
            self.save_voice_settings()

            self.log_message("Voice settings reset to defaults (Speed: 100%, Volume: 100%, Pitch: 0Hz)", "green")

        except Exception as e:
            self.log_message(f"Error resetting voice settings: {e}", "red")

    def create_text_widgets(self):
        """Create text widgets exactly as positioned in Qt Designer"""
        # Add text edit to widget (Text area in General tab)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setFrameStyle(0)  # Remove frame/border
        layout_text = QVBoxLayout(self.widget)
        layout_text.addWidget(self.text_edit)
        self.widget.setLayout(layout_text)

        # Add translator controls to General tab
        self.create_translator_controls()

        # Add log to widget_2 (App Log in Log tab)
        from PyQt5.QtWidgets import QTextEdit
        self.log = QTextEdit()
        self.log.setFrameStyle(0)  # Remove frame/border
        self.log.setReadOnly(True)  # Make it read-only
        layout_log = QVBoxLayout(self.widget_2)
        layout_log.addWidget(self.log)
        self.widget_2.setLayout(layout_log)

    def create_translator_controls(self):
        """Setup translator controls from Qt Designer"""
        try:
            # Setup translate button and combo box from UI
            if hasattr(self, 'translateButton'):
                self.translateButton.clicked.connect(self.translate_text)
            if hasattr(self, 'translateLangComboBox'):
                self.translateLangComboBox.addItems(["English", "Russian", "Ukrainian", "Japanese"])
                self.translateLangComboBox.setCurrentText("English")
        except Exception as e:
            print(f"Translator controls setup error: {e}")

    def setup_combo_boxes(self):
        # Model combo box - Edge TTS only
        self.comboBox.addItems(["Edge TTS"])
        self.comboBox.setCurrentText("Edge TTS")

        # Language combo box
        self.comboBox_2.addItems(["English", "Russian", "Ukrainian", "Japanese"])
        self.comboBox_2.setCurrentText("English")

        # Voice combo box
        self.update_voice_options()

        # Connect changes
        self.comboBox_2.currentTextChanged.connect(self.update_voice_options)
        self.comboBox.currentTextChanged.connect(self.update_voice_options)

        # Setup settings combo boxes
        self.setup_settings_combo_boxes()

        # Load saved settings
        self.load_saved_settings()

        # Note: Language localization is now applied in showEvent() after window is fully shown

    def setup_settings_combo_boxes(self):
        """Setup combo boxes in Settings tab"""
        try:
            # Theme/Style combo box - now contains styles instead of themes
            self.themeComboBox.addItems(["Light", "Dark"])
            self.themeComboBox.setCurrentText("Dark")
            self.themeComboBox.currentTextChanged.connect(self.change_style)
            
            # Language combo box for interface localization
            self.languageComboBox.addItems(["English", "Русский", "Українська"])
            self.languageComboBox.setCurrentText("English")
            self.languageComboBox.currentTextChanged.connect(self.change_language)
        except AttributeError as e:
            print(f"Settings combo box error: {e}")

    def load_saved_settings(self):
        """Load and apply saved settings"""
        settings = load_settings()
        
        # Load saved style
        saved_style = settings.get('selected_style', 'Dark')
        if saved_style in ["Light", "Dark"]:
            self.themeComboBox.setCurrentText(saved_style)
            # The change_style function will be called automatically due to the signal connection

        # Load saved language
        saved_language = settings.get('selected_language', 'English')
        if saved_language in ["English", "Русский", "Українська"]:
            self.languageComboBox.setCurrentText(saved_language)
            # The change_language function will be called automatically due to the signal connection

        # Load voice settings
        self.voice_speed = settings.get('voice_speed', 1.0)
        self.voice_volume = settings.get('voice_volume', 100)
        self.voice_pitch = settings.get('voice_pitch', 0)

        # Update UI elements if they exist
        if hasattr(self, 'speed_slider') and self.speed_slider:
            self.speed_slider.setValue(int(self.voice_speed * 100))
        if hasattr(self, 'volume_slider') and self.volume_slider:
            self.volume_slider.setValue(self.voice_volume)
        if hasattr(self, 'pitch_slider') and self.pitch_slider:
            self.pitch_slider.setValue(self.voice_pitch)

    def change_style(self):
        """Change style based on combo box selection"""
        style = self.themeComboBox.currentText()
        self.log_message(f"Applying style: {style}", "pink")
        
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
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                    gridline-color: #CCCCCC;
                }
                QTableWidget::item {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QTableWidget::item:selected {
                    background-color: #0078D4;
                    color: #FFFFFF;
                }
                """
                self.setStyleSheet(default_css)
                # Reset title bar to default
                try:
                    hwnd = get_hwnd_from_widget(self)
                    if hwnd:
                        set_title_bar_color(hwnd, False)  # Light title bar
                except:
                    pass
                self.log_message("Applied light style with larger fonts", "green")
            elif style == "Dark":
                # Map style names to file names
                style_files = {
                    "Dark": "ogidark.css"
                }
                style_file = style_files.get(style, "ogidark.css")
                style_path = os.path.join(os.path.dirname(__file__), 'styles', style_file)
                if os.path.exists(style_path):
                    with open(style_path, 'r', encoding='utf-8') as f:
                        stylesheet = f.read()
                    # Apply to main window
                    self.setStyleSheet(stylesheet)
                    
                    # Set title bar color to match theme
                    try:
                        hwnd = get_hwnd_from_widget(self)
                        if hwnd:
                            is_dark = style == "Dark"
                            set_title_bar_color(hwnd, is_dark)
                    except:
                        pass
                    
                    self.log_message(f"Applied {style} style successfully", "green")
                else:
                    self.log_message(f"Style file {style_file} not found", "red")
            else:
                style_file = os.path.join(os.path.dirname(__file__), 'styles', f'{style}.qss')
                if os.path.exists(style_file):
                    with open(style_file, 'r', encoding='utf-8') as f:
                        stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
                    # Reset title bar to default for other themes
                    try:
                        hwnd = get_hwnd_from_widget(self)
                        if hwnd:
                            set_title_bar_color(hwnd, False)
                    except:
                        pass
                    self.log_message(f"Applied {style} style successfully", "green")
                else:
                    self.log_message(f"Style file {style}.qss not found", "red")
            
            # Save the selected style
            settings = load_settings()
            settings['selected_style'] = style
            save_settings(settings)
            
        except Exception as e:
            self.log_message(f"Error applying style {style}: {e}", "red")

    def change_language(self):
        """Change interface language based on combo box selection"""
        language = self.languageComboBox.currentText()
        self.log_message(f"Changing interface language to: {language}", "blue")
        
        try:
            # Save the selected language
            settings = load_settings()
            settings['selected_language'] = language
            save_settings(settings)
            
            # Apply language changes to UI elements
            self.apply_language_localization(language)
            
            self.log_message(f"Interface language changed to {language}", "green")
            
        except Exception as e:
            self.log_message(f"Error changing language to {language}: {e}", "red")

    def apply_language_localization(self, language):
        """Apply language localization to UI elements"""
        # Use the LocalizationManager to apply localization
        self.localization_manager.apply_localization(self, language)

    def update_voice_options(self):
        """Update voice options based on selected language and model"""
        model = self.comboBox.currentText()
        language = self.comboBox_2.currentText()
        self.comboBox_3.clear()
        if model == "Edge TTS":
            if language == "English":
                self.comboBox_3.addItems(["Male", "Female"])
            elif language == "Russian":
                self.comboBox_3.addItems(["Male", "Female"])
            elif language == "Ukrainian":
                self.comboBox_3.addItems(["Male", "Female"])
            elif language == "Japanese":
                self.comboBox_3.addItems(["Male", "Female"])
        self.comboBox_3.setCurrentText("Female")

    def import_text(self):
        self.general_tab_manager.import_text()

    def connect_buttons(self):
        """Connect all buttons to their functions"""
        try:
            self.pushButton.clicked.connect(self.import_text)  # Import Text
            self.pushButton_2.clicked.connect(self.play_selected)  # Play Text
            self.pushButton_3.clicked.connect(self.save_to_audio)  # Save Audio
            self.pushButton_4.clicked.connect(self.open_result_folder)  # Open Result (General tab)
            self.pushButton_5.clicked.connect(self.copy_log)  # Copy Log
            self.pushButton_6.clicked.connect(self.clear_log)  # Clear Log
            self.pushButton_7.clicked.connect(self.open_result_folder)  # Open Result (Batch tab)
            self.supportButton.clicked.connect(self.open_support_link)  # Support Author

            # Connect reset voice settings button
            if hasattr(self, 'resetVoiceSettingsButton'):
                self.resetVoiceSettingsButton.clicked.connect(self.reset_voice_settings)

        except AttributeError as e:
            print(f"AttributeError: {e}")

    def get_selected_voice(self):
        model = self.comboBox.currentText()
        language = self.comboBox_2.currentText()
        voice_type = self.comboBox_3.currentText()
        if model == "Edge TTS":
            voice_map = {
                "English": {"Male": "en-US-ZiraNeural", "Female": "en-US-AriaNeural"},
                "Russian": {"Male": "ru-RU-DmitryNeural", "Female": "ru-RU-SvetlanaNeural"},
                "Ukrainian": {"Male": "uk-UA-OstapNeural", "Female": "uk-UA-PolinaNeural"},
                "Japanese": {"Male": "ja-JP-KeitaNeural", "Female": "ja-JP-NanamiNeural"}
            }
            return voice_map.get(language, {}).get(voice_type, "en-US-AriaNeural")
        return "en-US-AriaNeural"

    def play_selected(self):
        self.general_tab_manager.play_selected()

    def save_to_audio(self):
        self.general_tab_manager.save_to_audio()

    def translate_text(self):
        """Translate text using configured translation service"""
        self.general_tab_manager.translate_text()

    def generate_filename(self, is_example=False):
        model = self.comboBox.currentText()
        language = self.comboBox_2.currentText()
        voice_type = self.comboBox_3.currentText()
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

    def show_progress_bar(self):
        """Show progress bar during TTS operations"""
        if hasattr(self, 'progressBar'):
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            self.progressBar.setFormat("Starting...")

    def hide_progress_bar(self):
        """Hide progress bar after TTS operations"""
        if hasattr(self, 'progressBar'):
            self.progressBar.setVisible(False)
            self.progressBar.setValue(0)
            self.progressBar.setFormat("")

    def update_progress(self, value):
        """Update progress bar value"""
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(value)
            if value < 25:
                self.progressBar.setFormat("Initializing...")
            elif value < 50:
                self.progressBar.setFormat("Preparing voice...")
            elif value < 90:
                self.progressBar.setFormat("Generating speech...")
            elif value < 100:
                self.progressBar.setFormat("Saving...")
            else:
                self.progressBar.setFormat("Completed!")

    def on_tts_finished(self, msg):
        """Handle TTS completion"""
        self.log_message(msg, "green")
        if hasattr(self, 'progressBar'):
            self.progressBar.setValue(100)
            self.progressBar.setFormat("Completed!")
            # Hide progress bar after 2 seconds
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.hide_progress_bar)

    def copy_log(self):
        """Копирование логов в буфер обмена"""
        if hasattr(self, 'log') and self.log:
            clipboard = QApplication.clipboard()
            if clipboard:
                # Get plain text from QTextEdit
                plain_text = self.log.toPlainText()
                clipboard.setText(plain_text)
                self.log_message("Log copied to clipboard", "green")
            else:
                self.log_message("Clipboard not available", "red")
        else:
            self.log_message("Log widget not available", "red")

    def clear_log(self):
        """Очистка логов"""
        if hasattr(self, 'log') and self.log:
            self.log.clear()
            self.log_message("Log cleared", "blue")
        else:
            self.log_message("Log widget not available", "red")

    def open_result_folder(self):
        if getattr(sys, 'frozen', False):
            # Running as packaged exe - use exe directory
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running in development - use current directory (contains main.py)
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        output_dir = os.path.join(base_dir, 'tts_audio')
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            self.log_message("tts_audio folder does not exist yet", "red")

    def open_support_link(self):
        """Open Monobank support link in default browser"""
        monobank_url = "https://send.monobank.ua/jar/69c8gYDdWB"
        try:
            webbrowser.open(monobank_url)
            self.log_message("Opened support link in browser", "green")
        except Exception as e:
            self.log_message(f"Failed to open support link: {e}", "red")

    def log_message(self, message, color="black"):
        """Логирование сообщений"""
        if hasattr(self, 'log') and self.log:
            # For QTextEdit, we can use HTML for colors
            color_map = {
                "green": "#00AA00",
                "red": "#AA0000",
                "blue": "#FF1493",
                "pink": "#FF1493",
                "orange": "#FFA500",
                "yellow": "#AAAA00",
                "purple": "#AA00AA",
                "black": "#000000",
                "white": "#FFFFFF"
            }
            html_color = color_map.get(color, "#000000")
            html_message = f'<span style="color: {html_color};">{message}</span>'
            self.log.append(html_message)
        else:
            # Fallback to console
            print(f"[{color.upper()}] {message}")

    def save_voice_settings(self):
        """Save voice settings to settings file"""
        try:
            settings = load_settings()
            settings['voice_speed'] = self.voice_speed
            settings['voice_volume'] = self.voice_volume
            settings['voice_pitch'] = self.voice_pitch
            save_settings(settings)
        except Exception as e:
            self.log_message(f"Error saving voice settings: {e}", "red")

    def batch_import_files(self):
        self.batch_tab_manager.batch_import_files()

    def update_batch_ui(self):
        self.batch_tab_manager.update_batch_ui()

    def clear_batch_list(self):
        self.batch_tab_manager.clear_batch_list()

    def batch_process_files(self):
        self.batch_tab_manager.batch_process_files()

    def process_next_batch_file(self):
        self.batch_tab_manager.process_next_batch_file()

    def get_selected_voice_for_batch(self, file_info):
        return self.batch_tab_manager.get_selected_voice_for_batch(file_info)

    def update_batch_progress(self, value):
        self.batch_tab_manager.update_batch_progress(value)

    def on_batch_file_finished(self, msg):
        self.batch_tab_manager.on_batch_file_finished(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
