import os
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from core.settings import load_settings, save_settings

class ImgToTextTabManager:
    """Manager for IMG to Text (OCR) tab functionality"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.selected_image = None
        self.extracted_text = ""

    def setup_ui(self):
        """Setup UI elements from Qt Designer"""
        try:
            # Connect buttons if they exist
            if hasattr(self.main_window, 'selectImageButton'):
                self.main_window.selectImageButton.clicked.connect(self.select_image)

            if hasattr(self.main_window, 'extractTextButton'):
                self.main_window.extractTextButton.clicked.connect(self.extract_text_from_image)

            if hasattr(self.main_window, 'copyExtractedTextButton'):
                self.main_window.copyExtractedTextButton.clicked.connect(self.copy_extracted_text)

            if hasattr(self.main_window, 'saveExtractedTextButton'):
                self.main_window.saveExtractedTextButton.clicked.connect(self.save_extracted_text)

            # Setup OCR service combo box
            if hasattr(self.main_window, 'ocrServiceComboBox'):
                self.main_window.ocrServiceComboBox.addItems(["Google Vision API", "Azure Computer Vision"])
                self.main_window.ocrServiceComboBox.setCurrentText("Azure Computer Vision")
                # Connect service change to update status
                self.main_window.ocrServiceComboBox.currentTextChanged.connect(self.update_api_key_status)

            # Setup API key input with status monitoring
            if hasattr(self.main_window, 'ocrApiKeyInput'):
                self.main_window.ocrApiKeyInput.textChanged.connect(self.update_api_key_status)
                self.main_window.ocrApiKeyInput.textChanged.connect(self.save_ocr_settings)
            if hasattr(self.main_window, 'azureEndpointInput'):
                self.main_window.azureEndpointInput.textChanged.connect(self.save_ocr_settings)

            # Load saved settings
            self.load_ocr_settings()

        except Exception as e:
            print(f"OCR UI setup error: {e}")

    def select_image(self):
        """Select image file for OCR processing"""
        program_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Image File",
            program_dir,
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )

        if file_path:
            self.selected_image = file_path
            filename = os.path.basename(file_path)

            # Update image label
            if hasattr(self.main_window, 'selectedImageLabel'):
                self.main_window.selectedImageLabel.setText(f"Selected: {filename}")

            self.main_window.log_message(f"Image selected: {filename}", "green")

            # Auto-extract text if API key is available
            if self._has_api_key():
                self.extract_text_from_image()
            else:
                self.main_window.log_message("OCR API key not configured. Please set it up in Settings.", "orange")

    def extract_text_from_image(self):
        """Extract text from selected image using OCR API"""
        if not self.selected_image:
            self.main_window.log_message("Please select an image first", "red")
            return

        if not self._has_api_key():
            QMessageBox.warning(
                self.main_window,
                "API Key Required",
                "Please configure OCR API key in Settings first."
            )
            return

        self.main_window.log_message("Extracting text from image...", "blue")

        try:
            # Get selected OCR service
            service = self.main_window.ocrServiceComboBox.currentText() if hasattr(self.main_window, 'ocrServiceComboBox') else "Google Vision API"
            api_key = self.main_window.ocrApiKeyInput.text() if hasattr(self.main_window, 'ocrApiKeyInput') else ""

            if service == "Google Vision API":
                self.extracted_text = self._extract_with_google_vision(api_key)
            elif service == "Azure Computer Vision":
                self.extracted_text = self._extract_with_azure_vision(api_key)
            elif service == "Tesseract (Local)":
                self.extracted_text = self._extract_with_tesseract()
            else:
                raise ValueError(f"Unsupported OCR service: {service}")

            self._update_text_display()
            self.main_window.log_message(f"Text extracted successfully ({len(self.extracted_text)} characters)", "green")

        except Exception as e:
            error_msg = f"OCR failed: {str(e)}"
            self.main_window.log_message(error_msg, "red")
            QMessageBox.critical(self.main_window, "OCR Error", error_msg)

    def copy_extracted_text(self):
        """Copy extracted text to clipboard"""
        if not self.extracted_text:
            self.main_window.log_message("No text to copy", "orange")
            return

        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.extracted_text)
            self.main_window.log_message("Extracted text copied to clipboard", "green")
        else:
            self.main_window.log_message("Clipboard not available", "red")

    def save_extracted_text(self):
        """Save extracted text to file"""
        if not self.extracted_text:
            self.main_window.log_message("No text to save", "orange")
            return

        program_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Extracted Text",
            program_dir,
            "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.extracted_text)
                self.main_window.log_message(f"Text saved to: {os.path.basename(file_path)}", "green")
            except Exception as e:
                self.main_window.log_message(f"Failed to save text: {e}", "red")

    def clear_all(self):
        """Clear selected image and extracted text"""
        self.selected_image = None
        self.extracted_text = ""

        # Clear UI elements
        if hasattr(self.main_window, 'selectedImageLabel'):
            self.main_window.selectedImageLabel.setText("No image selected")

        if hasattr(self.main_window, 'extractedTextEdit'):
            self.main_window.extractedTextEdit.clear()

        self.main_window.log_message("OCR data cleared", "blue")

    def _has_api_key(self):
        """Check if OCR API key is configured"""
        settings = load_settings()
        return bool(settings.get('ocr_api_key', ''))

    def _update_text_display(self):
        """Update text display widget with extracted text"""
        if hasattr(self.main_window, 'extractedTextEdit'):
            self.main_window.extractedTextEdit.setPlainText(self.extracted_text)

    def setup_ocr_ui(self):
        """Setup OCR UI elements"""
        try:
            # Connect buttons if they exist
            if hasattr(self.main_window, 'ocrSelectImageBtn'):
                self.main_window.ocrSelectImageBtn.clicked.connect(self.select_image)

            if hasattr(self.main_window, 'ocrExtractBtn'):
                self.main_window.ocrExtractBtn.clicked.connect(self.extract_text_from_image)

            if hasattr(self.main_window, 'ocrCopyBtn'):
                self.main_window.ocrCopyBtn.clicked.connect(self.copy_extracted_text)

            if hasattr(self.main_window, 'ocrSaveBtn'):
                self.main_window.ocrSaveBtn.clicked.connect(self.save_extracted_text)

            if hasattr(self.main_window, 'ocrClearBtn'):
                self.main_window.ocrClearBtn.clicked.connect(self.clear_all)

        except Exception as e:
            print(f"OCR UI setup error: {e}")

    def load_ocr_settings(self):
        """Load OCR settings"""
        settings = load_settings()
        service = settings.get('ocr_service', 'Azure Computer Vision')
        api_key = settings.get('ocr_api_key', '')
        azure_endpoint = settings.get('azure_endpoint', 'https://westeurope.api.cognitive.microsoft.com/')

        if hasattr(self.main_window, 'ocrServiceComboBox'):
            # Always default to Azure Computer Vision
            self.main_window.ocrServiceComboBox.setCurrentText("Azure Computer Vision")
        if hasattr(self.main_window, 'ocrApiKeyInput'):
            self.main_window.ocrApiKeyInput.setText(api_key)
        if hasattr(self.main_window, 'azureEndpointInput'):
            self.main_window.azureEndpointInput.setText(azure_endpoint)

    def save_ocr_settings(self):
        """Save OCR settings"""
        settings = load_settings()
        
        if hasattr(self.main_window, 'ocrServiceComboBox'):
            settings['ocr_service'] = self.main_window.ocrServiceComboBox.currentText()
        if hasattr(self.main_window, 'ocrApiKeyInput'):
            settings['ocr_api_key'] = self.main_window.ocrApiKeyInput.text().strip()
        if hasattr(self.main_window, 'azureEndpointInput'):
            settings['azure_endpoint'] = self.main_window.azureEndpointInput.text().strip()
        
        save_settings(settings)

    def update_api_key_status(self):
        """Update API key status icon based on current input and service"""
        if not hasattr(self.main_window, 'ocrApiKeyStatusLabel') or not hasattr(self.main_window, 'ocrApiKeyInput'):
            return

        api_key = self.main_window.ocrApiKeyInput.text().strip()
        service = self.main_window.ocrServiceComboBox.currentText() if hasattr(self.main_window, 'ocrServiceComboBox') else "Google Vision API"

        # Default status: empty field
        if not api_key:
            self.main_window.ocrApiKeyStatusLabel.setText("⭕")
            self.main_window.ocrApiKeyStatusLabel.setToolTip("API Key Status: No key entered")
            return

        # Test the key asynchronously (don't block UI)
        try:
            if service == "Google Vision API":
                success = self._test_google_vision_key(api_key)
            elif service == "Azure Computer Vision":
                success = self._test_azure_vision_key(api_key)
            elif service == "Tesseract (Local)":
                success = self._test_tesseract_setup()
            else:
                success = False

            if success:
                self.main_window.ocrApiKeyStatusLabel.setText("✅")
                self.main_window.ocrApiKeyStatusLabel.setToolTip("API Key Status: Valid")
            else:
                self.main_window.ocrApiKeyStatusLabel.setText("❌")
                self.main_window.ocrApiKeyStatusLabel.setToolTip("API Key Status: Invalid")

        except Exception as e:
            # On error, show neutral status
            self.main_window.ocrApiKeyStatusLabel.setText("⭕")
            self.main_window.ocrApiKeyStatusLabel.setToolTip(f"API Key Status: Error - {str(e)}")

    def test_ocr_api_key(self):
        """Test OCR API key validity (legacy method, kept for compatibility)"""
        if not hasattr(self.main_window, 'ocrServiceComboBox') or not hasattr(self.main_window, 'ocrApiKeyInput'):
            self.main_window.log_message("OCR UI elements not available", "red")
            return

        service = self.main_window.ocrServiceComboBox.currentText()
        api_key = self.main_window.ocrApiKeyInput.text().strip()

        if not api_key:
            QMessageBox.warning(self.main_window, "API Key Required", "Please enter an API key first.")
            return

        self.main_window.log_message(f"Testing {service} API key...", "blue")

        try:
            if service == "Google Vision API":
                success = self._test_google_vision_key(api_key)
            elif service == "Azure Computer Vision":
                success = self._test_azure_vision_key(api_key)
            elif service == "Tesseract (Local)":
                success = self._test_tesseract_setup()
            else:
                raise ValueError(f"Unsupported OCR service: {service}")

            if success:
                QMessageBox.information(self.main_window, "API Key Valid", f"{service} API key is valid and working!")
                self.main_window.log_message(f"{service} API key test successful", "green")
            else:
                QMessageBox.warning(self.main_window, "API Key Invalid", f"{service} API key test failed. Please check your key.")
                self.main_window.log_message(f"{service} API key test failed", "red")

        except Exception as e:
            QMessageBox.critical(self.main_window, "API Key Test Error", f"Error testing API key: {str(e)}")
            self.main_window.log_message(f"API key test error: {e}", "red")

    def _test_google_vision_key(self, api_key):
        """Test Google Vision API key by making a simple request"""
        try:
            import requests

            # Create a minimal test request (empty image detection)
            test_data = {
                "requests": [{
                    "image": {
                        "content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # 1x1 transparent PNG
                    },
                    "features": [{
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }]
                }]
            }

            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=test_data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                # Check if we got a valid response (even if no text found)
                if 'responses' in result and len(result['responses']) > 0:
                    return True

            # Check for specific error messages
            if response.status_code == 400:
                error_data = response.json()
                if 'error' in error_data:
                    error_message = error_data['error'].get('message', '')
                    if 'API key' in error_message:
                        return False

            return False

        except ImportError:
            raise Exception("requests library not installed")
        except Exception as e:
            raise Exception(f"Google Vision API test failed: {str(e)}")

    def _test_azure_vision_key(self, api_key):
        """Test Azure Computer Vision API key"""
        try:
            import requests
            from PIL import Image
            import io

            # Get Azure endpoint from settings
            settings = load_settings()
            azure_endpoint = settings.get('azure_endpoint', 'https://westeurope.api.cognitive.microsoft.com/').rstrip('/')
            
            # Create a minimal test image (1x1 pixel)
            test_image = Image.new('RGB', (1, 1), color='white')
            img_byte_arr = io.BytesIO()
            test_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Try to make a request (this will fail with invalid image, but test auth)
            headers = {
                'Ocp-Apim-Subscription-Key': api_key,
                'Content-Type': 'application/octet-stream'
            }

            url = f"{azure_endpoint}/vision/v3.2/analyze?visualFeatures=Categories"
            response = requests.post(url, headers=headers, data=img_byte_arr, timeout=10)

            # If we get 200 or even 400 (bad request), key is valid
            # If 401/403, key is invalid
            if response.status_code in [200, 400, 415]:
                return True
            elif response.status_code in [401, 403]:
                return False
            else:
                # For other errors, assume key might be valid but service issue
                return True

        except ImportError:
            raise Exception("Required libraries not installed. Run: pip install requests pillow")
        except requests.exceptions.RequestException as e:
            # Network error, but key format might be ok
            raise Exception(f"Network error testing Azure key: {str(e)}")
        except Exception as e:
            raise Exception(f"Azure Computer Vision key test error: {str(e)}")

    def _test_tesseract_setup(self):
        """Test Tesseract OCR setup"""
        try:
            import pytesseract
            # Try to get tesseract version
            version = pytesseract.get_tesseract_version()
            return version is not None
        except ImportError:
            raise Exception("Tesseract OCR not installed. Run: pip install pytesseract")
        except Exception as e:
            raise Exception(f"Tesseract setup test failed: {str(e)}")

    def _extract_with_google_vision(self, api_key):
        """Extract text using Google Vision API"""
        try:
            from google.cloud import vision
            import io
            import json
            import base64

            # For Google Vision API, we need to use REST API with API key
            # since the Python client requires service account credentials

            # Read image and encode to base64
            with open(self.selected_image, 'rb') as image_file:
                content = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare request
            request_data = {
                "requests": [{
                    "image": {
                        "content": content
                    },
                    "features": [{
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }]
                }]
            }

            # Make API request
            import requests
            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=request_data, headers=headers)
            response.raise_for_status()

            result = response.json()

            # Extract text
            if 'responses' in result and result['responses']:
                response_data = result['responses'][0]
                if 'textAnnotations' in response_data and response_data['textAnnotations']:
                    return response_data['textAnnotations'][0]['description'].strip()
                elif 'error' in response_data:
                    raise Exception(f"Vision API error: {response_data['error']['message']}")
                else:
                    return "No text found in image"
            else:
                raise Exception("Invalid API response")

        except ImportError:
            raise Exception("Required libraries not installed. Run: pip install google-cloud-vision requests")
        except Exception as e:
            raise Exception(f"Google Vision API error: {str(e)}")

    def _extract_with_azure_vision(self, api_key):
        """Extract text using Azure Computer Vision API"""
        try:
            import requests

            # Get Azure endpoint from settings
            settings = load_settings()
            azure_endpoint = settings.get('azure_endpoint', 'https://westeurope.api.cognitive.microsoft.com/').rstrip('/')

            # Read image
            with open(self.selected_image, 'rb') as image_file:
                content = image_file.read()

            # Azure Computer Vision OCR API
            url = f"{azure_endpoint}/vision/v3.2/ocr"

            headers = {
                'Ocp-Apim-Subscription-Key': api_key,
                'Content-Type': 'application/octet-stream'
            }

            # Optional parameters for better OCR
            params = {
                'language': 'unk',  # Auto-detect language
                'detectOrientation': 'true'
            }

            # Make API request
            response = requests.post(url, headers=headers, params=params, data=content, timeout=30)
            response.raise_for_status()

            result = response.json()

            # Extract text from response
            extracted_text = ""
            if 'regions' in result:
                for region in result['regions']:
                    for line in region['lines']:
                        for word in line['words']:
                            extracted_text += word['text'] + ' '
                        extracted_text += '\n'
                return extracted_text.strip()
            else:
                return "No text found in image"

        except ImportError:
            raise Exception("Required libraries not installed. Run: pip install requests")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Azure Computer Vision API key")
            elif e.response.status_code == 403:
                raise Exception("Azure Computer Vision API access forbidden - check subscription")
            elif e.response.status_code == 429:
                raise Exception("Azure Computer Vision API rate limit exceeded")
            else:
                raise Exception(f"Azure Computer Vision API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error with Azure Computer Vision: {str(e)}")
        except Exception as e:
            raise Exception(f"Azure Computer Vision OCR error: {str(e)}")

    def _extract_with_tesseract(self):
        """Extract text using Tesseract OCR (local)"""
        try:
            import pytesseract
            from PIL import Image

            # Open image
            image = Image.open(self.selected_image)

            # Extract text
            text = pytesseract.image_to_string(image)

            return text.strip() if text.strip() else "No text found in image"

        except ImportError:
            raise Exception("Tesseract OCR not installed. Run: pip install pytesseract Pillow")
        except Exception as e:
            raise Exception(f"Tesseract OCR error: {str(e)}")