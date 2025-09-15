# OGI TTS v2.0 - Advanced Text-to-Speech Application

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15.9-green.svg)](https://pypi.org/project/PyQt5/)

A powerful desktop application for converting text to speech with advanced OCR, translation, and batch processing capabilities. Supports multiple languages, voices, and modern GUI with dark/light themes.

## ✨ New in v2.0

- 🌐 **Multi-language Interface**: English, Russian, Ukrainian
- 📷 **OCR Integration**: Google Vision API, Azure Computer Vision, Tesseract OCR
- 🌍 **Text Translation**: Microsoft Translator, Google Translate API
- 📦 **Batch Processing**: Convert multiple files at once
- 🎛️ **Voice Settings**: Speed, volume, and pitch controls
- 🎨 **Themes**: Light and Dark themes
- 💰 **Support Author**: Direct donation link
- 📱 **Modern UI**: Tabbed interface with improved UX

## 🚀 Quick Start

### For Users (Portable Version - Recommended)

1. **Download** the portable version: `OGI_TTS_v2.0_Portable.zip` from [Releases](https://github.com/Roflsockie/OGI-TTS-v2.0/releases)
2. **Extract** all files to any folder on your PC
3. **Run** `Run_OGI_TTS.bat` or double-click `OGI_TTS_v2.0.exe`
4. **Enjoy!** No installation required, works on any Windows 10/11 PC

### Alternative: Installer Version

1. **Download** `OGI_TTS_v2.0_Installer.exe` from releases
2. **Run** the installer and follow the setup wizard
3. **Launch** OGI TTS from Start Menu or Desktop shortcut

### For Developers

```bash
# Clone the repository
git clone https://github.com/Roflsockie/OGI-TTS-v2.0.git
cd OGI-TTS-v2.0

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📥 Downloads

### For End Users (Recommended)
**[OGI_TTS_v2.0_Portable.zip](https://github.com/Roflsockie/OGI-TTS-v2.0/releases/download/v2.0.0/OGI_TTS_v2.0_Portable.zip)** (58.7 MB)
- No installation required
- Works on any Windows 10/11 PC
- All dependencies included
- Just extract and run!

### For Developers
**[OGI_TTS_v2.0_Source.zip](https://github.com/Roflsockie/OGI-TTS-v2.0/releases/download/v2.0.0/OGI_TTS_v2.0_Source.zip)** (0.2 MB)
- Source code for customization
- Requires Python 3.11+
- Full development environment

## 📸 Screenshots

### Light Theme
![Light Theme](https://raw.githubusercontent.com/Roflsockie/OGI-TTS-v2.0/main/light.png)

### Dark Theme
![Dark Theme](https://raw.githubusercontent.com/Roflsockie/OGI-TTS-v2.0/main/dark.png)

## 📋 Features

### Core TTS Features
- **Multiple Languages**: Russian, English, Ukrainian, Japanese
- **Voice Options**: Male/Female voices for each language
- **File Import**: Support for .txt and .docx files
- **Auto Language Detection**: Automatically detects text language
- **Real-time Progress**: Progress bar with detailed status updates
- **Audio Output**: Saves generated speech as WAV files

### New Advanced Features (v2.0)
- **OCR Processing**: Extract text from images
  - Google Vision API integration
  - Azure Computer Vision support
  - Tesseract OCR as local fallback
- **Text Translation**: Translate text between languages
  - Microsoft Translator API
  - Google Translate API
- **Batch Processing**: Convert multiple files simultaneously
- **Voice Customization**: Adjust speed, volume, and pitch
- **Multi-language UI**: Interface in English, Russian, Ukrainian
- **Theme Support**: Light and Dark themes
- **Help System**: Built-in guides and tutorials

## 🛠️ System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.11+ (for development only)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Internet**: Required for TTS services and API calls

## 📖 Usage Guide

### Basic Text-to-Speech

1. **Import Text**: Click "Import Text" to select .txt or .docx files
2. **Choose Model**: Select "Edge TTS" (primary option)
3. **Select Language & Voice**: Choose from available options
4. **Voice Settings**: Adjust speed, volume, and pitch sliders
5. **Play Sample**: Enter text and click "Play Text" to preview
6. **Generate Audio**: Click "Save Audio" to convert full text
7. **Access Results**: Use "Open Result Folder" to view generated files

### OCR Text Extraction

1. Go to "IMG to Text" tab
2. Select OCR service (Google Vision, Azure Computer Vision, Tesseract)
3. Configure API keys if needed
4. Click "Select Image" to choose image file
5. Click "Extract Text" to process
6. Use "Save Text" or "Copy Text" for results

### Batch Processing

1. Go to "Batch" tab
2. Click "Import Files" to select multiple .txt/.docx files
3. Configure default settings (model, language, voice)
4. Click "Convert" to process all files
5. Monitor progress and access results

### Translation

1. Enter text in the main text area
2. Select target language from dropdown
3. Click "Translate" button
4. Translated text appears in the text area

## 🎯 Supported Languages & Voices

| Language | Male Voice | Female Voice |
|----------|------------|--------------|
| Russian | Dmitry | Svetlana |
| English | Zira | Aria |
| Ukrainian | Ostap | Polina |
| Japanese | Keita | Nanami |

## 🔧 Configuration

### API Keys Setup (Optional)

For full functionality, configure API keys in Settings:

#### Google Cloud Vision API (OCR)
1. Create Google Cloud project
2. Enable Vision API
3. Create service account key
4. Set `GOOGLE_APPLICATION_CREDENTIALS`

#### Azure Computer Vision (OCR)
1. Create Azure Cognitive Services resource
2. Get endpoint and key
3. Configure in application settings

#### Microsoft Translator
1. Create Azure Cognitive Services resource
2. Get endpoint and key
3. Configure in application settings

### Voice Settings
- **Speed**: 0.5x to 2.0x (default: 1.0x)
- **Volume**: 0% to 100% (default: 100%)
- **Pitch**: -50Hz to +50Hz (default: 0Hz)

## 🏗️ Technical Details

- **Framework**: Python 3.11 + PyQt5
- **TTS Engine**: Microsoft Edge TTS
- **OCR Engines**: Google Vision, Azure Computer Vision, Tesseract
- **Translation**: Microsoft Translator, Google Translate APIs
- **Build Tool**: PyInstaller for portable executable
- **File Size**: ~60MB (includes all dependencies)
- **Architecture**: Modular design with separate UI components

## 📁 Project Structure

```
ogi-tts-v2/
├── main.py                 # Main application entry point
├── main_window.ui          # Qt Designer UI file
├── requirements.txt        # Python dependencies
├── core/                   # Core functionality
│   ├── localization.py     # Multi-language support
│   ├── settings.py         # Settings management
│   └── tts_worker.py       # TTS processing
├── ui/                     # UI components
│   ├── general_tab.py      # General tab logic
│   ├── batch_tab.py        # Batch processing
│   ├── img_to_text_tab.py  # OCR functionality
│   └── settings_tab.py     # Settings management
├── styles/                 # UI themes
├── guides/                 # Help documentation
├── custom_models/          # Voice models
└── tts_audio/              # Output directory
```

## 🔒 API Keys Security

The application stores API keys locally in settings. For security:
- Never share your settings.json file
- Use environment variables for sensitive keys in production
- Rotate API keys regularly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Support the Author

If you find this project useful, consider supporting the author:
- **[Monobank](https://send.monobank.ua/jar/69c8gYDdWB)** - Direct donation link
- **GitHub Sponsor**: Coming soon

## 📞 Contact

For issues, feature requests, or questions:
- **[Report Bugs](https://github.com/Roflsockie/OGI-TTS-v2.0/issues)** - GitHub Issues
- **[Discussions](https://github.com/Roflsockie/OGI-TTS-v2.0/discussions)** - Community support
- **Built-in Help** - Accessible from the application

---

**Created with ❤️ by Roflsockie**

*OGI TTS v2.0 - Making speech synthesis simple and powerful*