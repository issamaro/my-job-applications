import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"

SUPPORTED_LANGUAGES = ("en", "fr", "nl")

MONTHS = {
    "en": {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    },
    "fr": {
        1: "Janv", 2: "Fév", 3: "Mars", 4: "Avr", 5: "Mai", 6: "Juin",
        7: "Juil", 8: "Août", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Déc"
    },
    "nl": {
        1: "Jan", 2: "Feb", 3: "Mrt", 4: "Apr", 5: "Mei", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
    }
}


def load_translations(language: str = "en") -> dict:
    """Load translations for the given language.

    Falls back to English if language not found.
    """
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language '{language}', falling back to English")
        language = "en"

    translation_file = TRANSLATIONS_DIR / f"{language}.json"

    if not translation_file.exists():
        logger.warning(f"Translation file not found: {translation_file}, falling back to English")
        translation_file = TRANSLATIONS_DIR / "en.json"

    try:
        with open(translation_file, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load translations: {e}")
        return load_fallback_translations()


def load_fallback_translations() -> dict:
    """Return hardcoded English translations as fallback."""
    return {
        "summary": "Professional Summary",
        "experience": "Experience",
        "skills": "Skills",
        "education": "Education",
        "languages": "Languages",
        "projects": "Projects",
        "contact": "Contact",
        "present": "Present",
        "at": "at",
        "in": "in"
    }


def format_date(date_str: str | None, language: str = "en") -> str:
    """Format a YYYY-MM date string to localized format.

    Returns the localized "Present" label if date_str is None.
    """
    if date_str is None:
        translations = load_translations(language)
        return translations.get("present", "Present")

    try:
        year, month = date_str.split("-")
        month_num = int(month)
        month_names = MONTHS.get(language, MONTHS["en"])
        month_name = month_names.get(month_num, month)
        return f"{month_name} {year}"
    except (ValueError, AttributeError):
        return date_str
