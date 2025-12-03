"""
Translation manager for JSON-based i18n.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class TranslationManager:
  """Simple JSON-based translation manager."""

  _current_language: str = "en"
  _translations: Dict[str, str] = {}
  _fallback_translations: Dict[str, str] = {}

  @classmethod
  def _get_i18n_dir(cls) -> Path:
    """Get the i18n directory path."""
    return Path(__file__).resolve().parent

  @classmethod
  def _load_language_file(cls, lang: str) -> Dict[str, str]:
    """Load a language JSON file.

    Args:
      lang: Language code, e.g. "en", "zh-TW".

    Returns:
      Dict of translations. Returns empty dict if file not found.
    """
    i18n_dir = cls._get_i18n_dir()
    file_path = i18n_dir / f"{lang}.json"
    if not file_path.exists():
      print(f"[i18n] Translation file not found: {file_path}")
      return {}

    try:
      with file_path.open("r", encoding="utf-8") as f:
        data: Any = json.load(f)
        if isinstance(data, dict):
          return {str(k): str(v) for k, v in data.items()}
    except Exception as exc:  # noqa: BLE001
      print(f"[i18n] Failed to load translation file {file_path}: {exc}")

    return {}

  @classmethod
  def set_language(cls, lang: str, fallback_lang: str = "en") -> None:
    """Set the current language and load translations.

    Args:
      lang: Target language code.
      fallback_lang: Fallback language code (default: "en").
    """
    cls._current_language = lang
    cls._translations = cls._load_language_file(lang)
    cls._fallback_translations = (
      cls._load_language_file(fallback_lang) if fallback_lang != lang else cls._translations
    )
    print(f"[i18n] Language set to '{lang}', fallback '{fallback_lang}'")

  @classmethod
  def get_current_language(cls) -> str:
    """Get the current language code.

    Returns:
      Current language code, e.g. "en", "zh-TW".
    """
    return cls._current_language

  @classmethod
  def translate(cls, key: str, default: Optional[str] = None) -> str:
    """Translate a key using the current language.

    Args:
      key: Translation key, e.g. "main.button.click".
      default: Optional default value if key not found.

    Returns:
      Translated string or fallback/default/key.
    """
    if key in cls._translations:
      return cls._translations[key]

    if key in cls._fallback_translations:
      return cls._fallback_translations[key]

    if default is not None:
      return default

    # As a last resort, return the key itself
    return key


def t(key: str, default: Optional[str] = None) -> str:
  """Convenience function for translating a key.

  Args:
    key: Translation key.
    default: Optional default value.

  Returns:
    Translated string.
  """
  return TranslationManager.translate(key, default=default)
