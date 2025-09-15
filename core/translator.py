import requests
import json
import uuid
from typing import Optional, Dict, Any

class TranslatorError(Exception):
    """Custom exception for translation errors"""
    pass

class BaseTranslator:
    """Base class for translation services"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to target language"""
        raise NotImplementedError

    def test_key(self) -> bool:
        """Test if API key is valid"""
        raise NotImplementedError

class MicrosoftTranslator(BaseTranslator):
    """Microsoft Translator API implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.endpoint = "https://api.cognitive.microsofttranslator.com"
        self.location = "westeurope"  # Default location

    def translate(self, text: str, target_lang: str) -> str:
        """Translate text using Microsoft Translator API"""
        if not self.api_key:
            raise TranslatorError("API key is required")

        # Map language names to codes
        lang_codes = {
            "English": "en",
            "Russian": "ru",
            "Ukrainian": "uk",
            "Japanese": "ja"
        }

        target_code = lang_codes.get(target_lang, "en")

        path = '/translate'
        constructed_url = self.endpoint + path

        params = {
            'api-version': '3.0',
            'to': target_code
        }

        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
            'text': text
        }]

        try:
            response = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result and len(result) > 0 and 'translations' in result[0]:
                return result[0]['translations'][0]['text']
            else:
                raise TranslatorError("Invalid response format")

        except requests.exceptions.RequestException as e:
            raise TranslatorError(f"Translation request failed: {str(e)}")

    def test_key(self) -> bool:
        """Test Microsoft Translator API key"""
        try:
            # Test with a simple translation
            result = self.translate("Hello", "Russian")
            return len(result) > 0
        except:
            return False

class GoogleTranslator(BaseTranslator):
    """Google Cloud Translate API implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.endpoint = "https://translation.googleapis.com/language/translate/v2"

    def translate(self, text: str, target_lang: str) -> str:
        """Translate text using Google Cloud Translate API"""
        if not self.api_key:
            raise TranslatorError("API key is required")

        # Map language names to codes
        lang_codes = {
            "English": "en",
            "Russian": "ru",
            "Ukrainian": "uk",
            "Japanese": "ja"
        }

        target_code = lang_codes.get(target_lang, "en")

        params = {
            'q': text,
            'target': target_code,
            'key': self.api_key
        }

        try:
            response = requests.post(self.endpoint, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            if 'data' in result and 'translations' in result['data'] and len(result['data']['translations']) > 0:
                return result['data']['translations'][0]['translatedText']
            else:
                raise TranslatorError("Invalid response format")

        except requests.exceptions.RequestException as e:
            raise TranslatorError(f"Translation request failed: {str(e)}")

    def test_key(self) -> bool:
        """Test Google Cloud Translate API key"""
        try:
            # Test with a simple translation
            result = self.translate("Hello", "Russian")
            return len(result) > 0
        except:
            return False

class TranslatorManager:
    """Manager for translation services"""

    def __init__(self):
        self.services = {
            "Microsoft Translator": MicrosoftTranslator,
            "Google Cloud Translate": GoogleTranslator
        }

    def get_translator(self, service_name: str, api_key: str) -> BaseTranslator:
        """Get translator instance for specified service"""
        if service_name not in self.services:
            raise TranslatorError(f"Unknown service: {service_name}")

        return self.services[service_name](api_key)

    def get_service_descriptions(self, localization_manager=None) -> Dict[str, str]:
        """Get descriptions for all available services"""
        if localization_manager:
            return {
                "Microsoft Translator": localization_manager.get_text("microsoft_translator_desc"),
                "Google Cloud Translate": localization_manager.get_text("google_translate_desc")
            }
        else:
            # Fallback to default Russian descriptions
            return {
                "Microsoft Translator": (
                    "Бесплатный уровень: до 50 000 символов в месяц.\n"
                    "Для получения ключа зарегистрируйтесь на Azure Portal, "
                    "создайте ресурс Translator и скопируйте ключ из раздела «Ключи и эндпоинты».\n"
                    '<a href="https://portal.azure.com/" style="color: #0066CC;">Azure Portal</a> | '
                    '<a href="https://www.youtube.com/results?search_query=azure+translator+api+setup" style="color: #0066CC;">Видео гайд</a>\n'
                    "Введите ключ в поле ниже."
                ),
                "Google Cloud Translate": (
                    "Бесплатный уровень: до 50 000 символов в месяц.\n"
                    "Для получения ключа создайте проект в Google Cloud Console, "
                    "включите API Cloud Translation, создайте учетные данные (API key).\n"
                    '<a href="https://console.cloud.google.com/" style="color: #0066CC;">Google Cloud Console</a> | '
                    '<a href="https://www.youtube.com/results?search_query=google+cloud+translate+api+setup" style="color: #0066CC;">Видео гайд</a>\n'
                    "Введите ключ в поле ниже."
                )
            }