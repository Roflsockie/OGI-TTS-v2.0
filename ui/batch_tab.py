import os
import sys
from PyQt5.QtWidgets import QFileDialog, QPushButton, QListWidget, QLabel, QProgressBar, QComboBox, QTableWidget, QTableWidgetItem
from langdetect import detect
from docx import Document
from core.tts_worker import TTSWorker

class BatchTabManager:
    """Manager for Text to Audio (Batch) tab functionality"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.batch_files = []  # List of file info dictionaries
        self.batch_processing = False
        self.current_batch_index = 0
        
        # Setup batch UI elements
        self.setup_batch_ui()
        
        # Connect batch buttons
        self.connect_batch_buttons()

    def setup_batch_ui(self):
        """Setup batch processing UI elements"""
        try:
            # Find batch processing UI elements
            self.main_window.batchImportButton = self.main_window.findChild(QPushButton, "batchImportButton")
            self.main_window.batchProcessButton = self.main_window.findChild(QPushButton, "batchProcessButton")
            self.main_window.clearBatchListButton = self.main_window.findChild(QPushButton, "clearBatchListButton")
            self.main_window.batchFileTable = self.main_window.findChild(QTableWidget, "batchFileTable")
            self.main_window.batchStatusLabel = self.main_window.findChild(QLabel, "batchStatusLabel")
            self.main_window.batchProgressBar = self.main_window.findChild(QProgressBar, "batchProgressBar")
            self.main_window.batchInfoLabel = self.main_window.findChild(QLabel, "batchInfoLabel")
            self.main_window.batchModelComboBox = self.main_window.findChild(QComboBox, "batchModelComboBox")
            self.main_window.batchModelLabel = self.main_window.findChild(QLabel, "batchModelLabel")

            # Setup table column widths
            if self.main_window.batchFileTable:
                # Set column widths: File (wide), Language (medium), Model (medium), Voice (narrow)
                self.main_window.batchFileTable.setColumnWidth(0, 250)  # File column - widest
                self.main_window.batchFileTable.setColumnWidth(1, 100)  # Language column - medium
                self.main_window.batchFileTable.setColumnWidth(2, 100)  # Model column - medium
                self.main_window.batchFileTable.setColumnWidth(3, 80)   # Voice column - narrowest
                # Disable alternating row colors to avoid visibility issues with themes
                self.main_window.batchFileTable.setAlternatingRowColors(False)

            # Initialize UI state
            if self.main_window.batchStatusLabel:
                self.main_window.batchStatusLabel.setText("Files: 0 | Characters: 0")
            if self.main_window.batchProgressBar:
                self.main_window.batchProgressBar.setVisible(False)
            if self.main_window.batchProcessButton:
                self.main_window.batchProcessButton.setEnabled(False)

            # Setup model combo box
            if self.main_window.batchModelComboBox:
                self.main_window.batchModelComboBox.addItems(["Edge TTS"])
                self.main_window.batchModelComboBox.setCurrentText("Edge TTS")
                self.main_window.batchModelComboBox.currentTextChanged.connect(self.update_default_model)

        except Exception as e:
            print(f"Batch UI setup error: {e}")

    def update_default_model(self):
        """Update default model selection for batch processing"""
        if hasattr(self.main_window, 'batchModelComboBox') and self.main_window.batchModelComboBox:
            model = self.main_window.batchModelComboBox.currentText()
            self.main_window.log_message(f"Batch default model changed to: {model}", "blue")

            # Update existing files with new default model
            for file_info in self.batch_files:
                file_info['selected_model'] = model

            # Update UI to reflect changes
            self.update_batch_ui()

    def connect_batch_buttons(self):
        """Connect batch processing buttons"""
        try:
            if hasattr(self.main_window, 'batchImportButton') and self.main_window.batchImportButton:
                self.main_window.batchImportButton.clicked.connect(self.batch_import_files)
            if hasattr(self.main_window, 'batchProcessButton') and self.main_window.batchProcessButton:
                self.main_window.batchProcessButton.clicked.connect(self.batch_process_files)
            if hasattr(self.main_window, 'clearBatchListButton') and self.main_window.clearBatchListButton:
                self.main_window.clearBatchListButton.clicked.connect(self.clear_batch_list)
        except AttributeError as e:
            print(f"Batch button connection error: {e}")

    def batch_import_files(self):
        """Import multiple text files for batch processing"""
        # Use project root directory as default
        program_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        
        file_paths, _ = QFileDialog.getOpenFileNames(self.main_window, "Select Text Files", program_dir, "Text Files (*.txt *.docx)")

        if not file_paths:
            return

        total_chars = 0
        imported_count = 0

        for file_path in file_paths:
            try:
                # Read file content
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif file_path.endswith('.docx'):
                    doc = Document(file_path)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                else:
                    continue

                if not content.strip():
                    continue

                # Detect language
                try:
                    detected_lang = detect(content)
                    if detected_lang == 'ru':
                        lang = "Russian"
                    elif detected_lang == 'en':
                        lang = "English"
                    elif detected_lang == 'uk':
                        lang = "Ukrainian"
                    elif detected_lang == 'ja':
                        lang = "Japanese"
                    else:
                        lang = "English"
                except:
                    lang = "English"

                # Determine default model based on language
                default_model = "Edge TTS"
                if hasattr(self.main_window, 'batchModelComboBox') and self.main_window.batchModelComboBox:
                    default_model = self.main_window.batchModelComboBox.currentText()

                model = default_model

                # Set default voice based on language and model
                if model == "Edge TTS":
                    if lang == "English":
                        default_voice = "Female (Aria)"
                    elif lang == "Russian":
                        default_voice = "Female (Svetlana)"
                    elif lang == "Ukrainian":
                        default_voice = "Female (Polina)"
                    elif lang == "Japanese":
                        default_voice = "Female (Nanami)"
                    else:
                        default_voice = "Female (Aria)"

                # Add to batch list
                filename = os.path.basename(file_path)
                self.batch_files.append({
                    'file_path': file_path,
                    'filename': filename,
                    'content': content,
                    'detected_lang': lang,
                    'selected_model': model,
                    'selected_lang': lang,
                    'selected_voice': default_voice  # Use language-appropriate default voice
                })

                total_chars += len(content)
                imported_count += 1

                self.main_window.log_message(f"Imported: {filename} ({len(content)} chars, detected: {lang})", "green")

            except Exception as e:
                self.main_window.log_message(f"Error importing {os.path.basename(file_path)}: {e}", "red")

        # Update UI
        self.update_batch_ui()
        self.main_window.log_message(f"Batch import completed: {imported_count} files, {total_chars} total characters", "blue")

    def update_batch_ui(self):
        """Update batch processing UI elements"""
        if not hasattr(self.main_window, 'batchFileTable'):
            return

        # Update the table widget
        try:
            table = self.main_window.batchFileTable
            table.setRowCount(len(self.batch_files))
            
            for row, file_info in enumerate(self.batch_files):
                filename = file_info['filename']
                chars = len(file_info['content'])
                lang = file_info['detected_lang']
                model = file_info['selected_model']
                voice = file_info['selected_voice']
                
                # File name column
                file_item = QTableWidgetItem(f"{filename}\n({chars} chars)")
                file_item.setToolTip(f"File: {filename}\nCharacters: {chars}\nLanguage: {lang}")
                table.setItem(row, 0, file_item)
                
                # Language column
                lang_item = QTableWidgetItem(lang)
                table.setItem(row, 1, lang_item)
                
                # Model combo box column
                model_combo = QComboBox()
                model_combo.addItems(["Edge TTS"])
                model_combo.setCurrentText(model)
                model_combo.currentTextChanged.connect(lambda text, r=row: self.update_file_model(r, text))
                table.setCellWidget(row, 2, model_combo)
                
                # Voice combo box column
                voice_combo = QComboBox()
                self.update_voice_options_for_row(voice_combo, model, lang)
                voice_combo.setCurrentText(voice)
                voice_combo.currentTextChanged.connect(lambda text, r=row: self.update_file_voice(r, text))
                table.setCellWidget(row, 3, voice_combo)

        except Exception as e:
            print(f"Error updating batch table: {e}")
            return

        # Update status label
        total_chars = sum(len(f['content']) for f in self.batch_files)
        if hasattr(self.main_window, 'batchStatusLabel') and self.main_window.batchStatusLabel:
            try:
                self.main_window.batchStatusLabel.setText(f"Files: {len(self.batch_files)} | Characters: {total_chars}")
            except Exception as e:
                print(f"Error updating batch status label: {e}")

        # Enable/disable process button
        if hasattr(self.main_window, 'batchProcessButton') and self.main_window.batchProcessButton:
            try:
                self.main_window.batchProcessButton.setEnabled(len(self.batch_files) > 0)
            except Exception as e:
                print(f"Error enabling batch process button: {e}")

        # Estimate processing time (rough estimate: ~10 chars/second for TTS)
        if len(self.batch_files) > 0:
            estimated_time = total_chars / 10  # seconds
            time_str = f"~{estimated_time:.0f}s" if estimated_time < 60 else f"~{estimated_time/60:.1f}min"
            self.main_window.log_message(f"Estimated processing time: {time_str} for {len(self.batch_files)} files", "blue")

    def update_file_model(self, row, model):
        """Update model selection for a specific file"""
        if 0 <= row < len(self.batch_files):
            self.batch_files[row]['selected_model'] = model
            # Update voice options when model changes
            table = self.main_window.batchFileTable
            voice_combo = table.cellWidget(row, 3)
            if voice_combo:
                lang = self.batch_files[row]['detected_lang']
                self.update_voice_options_for_row(voice_combo, model, lang)
                # Reset voice to first available option
                if voice_combo.count() > 0:
                    voice_combo.setCurrentIndex(0)
                    self.batch_files[row]['selected_voice'] = voice_combo.currentText()

    def update_file_voice(self, row, voice):
        """Update voice selection for a specific file"""
        if 0 <= row < len(self.batch_files):
            self.batch_files[row]['selected_voice'] = voice

    def update_voice_options_for_row(self, voice_combo, model, lang):
        """Update available voice options for a combo box based on model and language"""
        voice_combo.clear()
        
        if model == "Edge TTS":
            if lang == "English":
                voice_combo.addItems(["Male (Zira)", "Female (Aria)"])
            elif lang == "Russian":
                voice_combo.addItems(["Male (Dmitry)", "Female (Svetlana)"])
            elif lang == "Ukrainian":
                voice_combo.addItems(["Male (Ostap)", "Female (Polina)"])
            elif lang == "Japanese":
                voice_combo.addItems(["Male (Keita)", "Female (Nanami)"])
            else:
                voice_combo.addItems(["Female (Aria)", "Male (Zira)"])

    def clear_batch_list(self):
        """Clear the batch file list"""
        self.batch_files.clear()
        if hasattr(self.main_window, 'batchFileTable'):
            self.main_window.batchFileTable.setRowCount(0)
        self.update_batch_ui()
        self.main_window.log_message("Batch file list cleared", "blue")

    def batch_process_files(self):
        """Process all files in batch"""
        if not self.batch_files:
            self.main_window.log_message("No files to process", "orange")
            return

        if self.batch_processing:
            self.main_window.log_message("Batch processing already in progress", "orange")
            return

        self.batch_processing = True
        self.main_window.log_message(f"Starting batch processing of {len(self.batch_files)} files...", "blue")

        # Show progress bar
        if hasattr(self.main_window, 'batchProgressBar') and self.main_window.batchProgressBar:
            self.main_window.batchProgressBar.setVisible(True)
            self.main_window.batchProgressBar.setValue(0)
            self.main_window.batchProgressBar.setMaximum(len(self.batch_files))

        # Disable buttons during processing
        if hasattr(self.main_window, 'batchProcessButton'):
            self.main_window.batchProcessButton.setEnabled(False)
        if hasattr(self.main_window, 'batchImportButton'):
            self.main_window.batchImportButton.setEnabled(False)
        if hasattr(self.main_window, 'clearBatchListButton'):
            self.main_window.clearBatchListButton.setEnabled(False)

        # Start batch processing
        self.current_batch_index = 0
        self.process_next_batch_file()

    def process_next_batch_file(self):
        """Process the next file in batch"""
        if self.current_batch_index >= len(self.batch_files):
            # Batch processing completed
            self.batch_processing = False
            self.main_window.log_message("Batch processing completed!", "green")

            # Hide progress bar
            if hasattr(self.main_window, 'batchProgressBar'):
                self.main_window.batchProgressBar.setVisible(False)

            # Re-enable buttons
            if hasattr(self.main_window, 'batchProcessButton'):
                self.main_window.batchProcessButton.setEnabled(True)
            if hasattr(self.main_window, 'batchImportButton'):
                self.main_window.batchImportButton.setEnabled(True)
            if hasattr(self.main_window, 'clearBatchListButton'):
                self.main_window.clearBatchListButton.setEnabled(True)

            return

        file_info = self.batch_files[self.current_batch_index]
        filename = file_info['filename']
        content = file_info['content']
        model = file_info['selected_model']
        lang = file_info['selected_lang']

        self.main_window.log_message(f"Processing file {self.current_batch_index + 1}/{len(self.batch_files)}: {filename}", "blue")

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
            self.main_window.log_message(f"Created output directory: {output_dir}", "blue")

        # Generate output filename
        lang_code = {
            "Russian": "ru",
            "English": "eng",
            "Ukrainian": "ua",
            "Japanese": "jp"
        }.get(lang, "unk")

        if model == "Edge TTS":
            model_tag = "edge"

        output_file = os.path.join(output_dir, f"batch_{self.current_batch_index + 1}_{lang_code}_{model_tag}_{os.path.splitext(filename)[0]}.wav")
        self.main_window.log_message(f"Output file: {output_file}", "blue")

        # Get voice for this file
        voice = self.get_selected_voice_for_batch(file_info)

        # Start TTS worker
        self.main_window.batch_worker = TTSWorker(content, voice, output_file,
                                    speed=self.main_window.voice_speed,
                                    volume=self.main_window.voice_volume,
                                    pitch=self.main_window.voice_pitch,
                                    model=model)
        self.main_window.batch_worker.progress.connect(self.update_batch_progress)
        self.main_window.batch_worker.log_signal.connect(lambda msg: self.main_window.log_message(f"[{filename}] {msg}", "blue"))
        self.main_window.batch_worker.finished.connect(self.on_batch_file_finished)
        self.main_window.batch_worker.start()

    def get_selected_voice_for_batch(self, file_info):
        """Get selected voice for batch file processing"""
        model = file_info['selected_model']
        lang = file_info['selected_lang']
        voice_type = file_info['selected_voice']

        if model == "Edge TTS":
            voice_map = {
                "English": {
                    "Male (Zira)": "en-US-ZiraNeural",
                    "Female (Aria)": "en-US-AriaNeural"
                },
                "Russian": {
                    "Male (Dmitry)": "ru-RU-DmitryNeural", 
                    "Female (Svetlana)": "ru-RU-SvetlanaNeural"
                },
                "Ukrainian": {
                    "Male (Ostap)": "uk-UA-OstapNeural",
                    "Female (Polina)": "uk-UA-PolinaNeural"
                },
                "Japanese": {
                    "Male (Keita)": "ja-JP-KeitaNeural",
                    "Female (Nanami)": "ja-JP-NanamiNeural"
                }
            }
            return voice_map.get(lang, {}).get(voice_type, "en-US-AriaNeural")
        return "en-US-AriaNeural"

    def update_batch_progress(self, value):
        """Update batch progress bar"""
        if hasattr(self.main_window, 'batchProgressBar') and self.main_window.batchProgressBar:
            # Update overall progress
            current_file_progress = value / 100.0
            overall_progress = (self.current_batch_index + current_file_progress) / len(self.batch_files) * 100
            self.main_window.batchProgressBar.setValue(int(overall_progress))

    def on_batch_file_finished(self, msg):
        """Handle completion of batch file processing"""
        filename = self.batch_files[self.current_batch_index]['filename']
        
        # Check if output file was created - use correct base directory for portable version
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
        lang_code = {
            "Russian": "ru",
            "English": "eng", 
            "Ukrainian": "ua",
            "Japanese": "jp"
        }.get(self.batch_files[self.current_batch_index]['selected_lang'], "unk")
        
        model = self.batch_files[self.current_batch_index]['selected_model']
        if model == "Edge TTS":
            model_tag = "edge"
            
        output_file = os.path.join(output_dir, f"batch_{self.current_batch_index + 1}_{lang_code}_{model_tag}_{os.path.splitext(filename)[0]}.wav")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            self.main_window.log_message(f"Completed: {filename} - {msg} (File saved: {file_size} bytes)", "green")
        else:
            self.main_window.log_message(f"Completed: {filename} - {msg} (WARNING: File not found at {output_file})", "orange")

        # Move to next file
        self.current_batch_index += 1
        self.process_next_batch_file()