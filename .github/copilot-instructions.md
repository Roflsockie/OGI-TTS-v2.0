# Copilot Instructions for OGI TTS New Interface

## Архитектура и компоненты
- Проект состоит из нескольких интерфейсов: PyQt (main.py), React (gai_studio/), и Python API (api.py).
- Основная логика TTS реализована в Python, интеграция с моделями — через custom_models/.
- React-интерфейс общается с Python API через HTTP (порт 5000).
- Файлы интерфейса: `main_window.ui` (Qt Designer), стили: `styles.qss`, `sun_valley_dark.qss`, `sun_valley_light.qss`.
- Модели и голоса хранятся в custom_models/ (поддержка разных языков и голосов).

## Запуск и рабочие сценарии
- Быстрый запуск: `python run_simple.py`.
- Диагностика и проверка зависимостей: `python launcher.py`.
- Интегрированная версия (React + API): `run_integrated.bat`.
- Оригинальный PyQt: `python main.py` или `run.bat`.
- Тестовый запуск: `python test_run.py`.
- Анализ интерфейса: `python interface_helper.py`.

## Зависимости
- Основные: PyQt5, edge-tts, langdetect, requests, Pillow.
- Установка: `pip install -r requirements.txt`.

## Ключевые паттерны и конвенции
- Выбор модели, языка и голоса — через combo boxes.
- Настройки TTS (скорость, громкость, тон) — через слайдеры.
- Логика работы с файлами: поддержка .txt и .docx.
- Переключение тем — через отдельный компонент.
- Логирование действий пользователя.

## Интеграция моделей
- custom_models/ содержит веса и конфиги для разных языков и голосов.
- Для японской модели Kokoro см. custom_models/jp_model/README.md.

## Примеры команд
- Запуск API: `python api.py`
- Запуск React: `npm run dev` (в gai_studio/)
- Генерация интерфейсных привязок: `python interface_helper.py`

## Важные файлы и директории
- main.py — точка входа PyQt интерфейса
- api.py — точка входа API
- custom_models/ — модели и голоса
- main_window.ui — дизайн интерфейса
- styles.qss, sun_valley_dark.qss, sun_valley_light.qss — стили
- requirements.txt — зависимости

## Советы для AI-агентов
- Всегда проверяйте, какой интерфейс/режим требуется пользователю.
- Для интеграции новых моделей добавляйте их в custom_models/ и обновляйте логику выбора.
- Для расширения интерфейса используйте Qt Designer (`main_window.ui`) или React-компоненты.
- Следите за совместимостью зависимостей и версий Python.

---
Документ обновлен 12.09.2025. Для уточнения архитектуры и паттернов см. README.md и custom_models/jp_model/README.md.
