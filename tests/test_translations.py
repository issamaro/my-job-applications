"""Tests for the translations service."""

import pytest
from services.translations import load_translations, format_date, MONTHS, SUPPORTED_LANGUAGES


class TestLoadTranslations:
    """Tests for load_translations function."""

    def test_load_english_translations(self):
        """English translations should load correctly."""
        translations = load_translations("en")
        assert translations["summary"] == "Professional Summary"
        assert translations["experience"] == "Experience"
        assert translations["skills"] == "Skills"
        assert translations["education"] == "Education"
        assert translations["languages"] == "Languages"
        assert translations["projects"] == "Projects"
        assert translations["present"] == "Present"

    def test_load_french_translations(self):
        """French translations should load correctly."""
        translations = load_translations("fr")
        assert translations["summary"] == "Profil Professionnel"
        assert translations["experience"] == "Expérience"
        assert translations["skills"] == "Compétences"
        assert translations["education"] == "Formation"
        assert translations["languages"] == "Langues"
        assert translations["projects"] == "Projets"
        assert translations["present"] == "Présent"

    def test_load_dutch_translations(self):
        """Dutch translations should load correctly."""
        translations = load_translations("nl")
        assert translations["summary"] == "Professioneel Profiel"
        assert translations["experience"] == "Werkervaring"
        assert translations["skills"] == "Vaardigheden"
        assert translations["education"] == "Opleiding"
        assert translations["languages"] == "Talen"
        assert translations["projects"] == "Projecten"
        assert translations["present"] == "Heden"

    def test_fallback_to_english_for_unknown_language(self):
        """Unknown language should fall back to English."""
        translations = load_translations("xx")
        assert translations["summary"] == "Professional Summary"
        assert translations["present"] == "Present"

    def test_all_translations_have_same_keys(self):
        """All translation files should have the same keys."""
        en = load_translations("en")
        fr = load_translations("fr")
        nl = load_translations("nl")

        assert set(en.keys()) == set(fr.keys()) == set(nl.keys())


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_english(self):
        """Date formatting in English."""
        assert format_date("2024-01", "en") == "Jan 2024"
        assert format_date("2024-06", "en") == "Jun 2024"
        assert format_date("2024-12", "en") == "Dec 2024"

    def test_format_date_french(self):
        """Date formatting in French."""
        assert format_date("2024-01", "fr") == "Janv 2024"
        assert format_date("2024-06", "fr") == "Juin 2024"
        assert format_date("2024-12", "fr") == "Déc 2024"

    def test_format_date_dutch(self):
        """Date formatting in Dutch."""
        assert format_date("2024-01", "nl") == "Jan 2024"
        assert format_date("2024-05", "nl") == "Mei 2024"
        assert format_date("2024-10", "nl") == "Okt 2024"

    def test_format_date_none_returns_present(self):
        """None date should return localized 'Present'."""
        assert format_date(None, "en") == "Present"
        assert format_date(None, "fr") == "Présent"
        assert format_date(None, "nl") == "Heden"

    def test_format_date_invalid_format_returns_original(self):
        """Invalid date format should return original string."""
        assert format_date("invalid", "en") == "invalid"
        assert format_date("2024", "en") == "2024"


class TestMonthsDict:
    """Tests for MONTHS dictionary."""

    def test_all_languages_have_12_months(self):
        """Each language should have all 12 months."""
        for lang in SUPPORTED_LANGUAGES:
            assert lang in MONTHS
            assert len(MONTHS[lang]) == 12
            for month_num in range(1, 13):
                assert month_num in MONTHS[lang]

    def test_months_are_non_empty_strings(self):
        """Each month name should be a non-empty string."""
        for lang in SUPPORTED_LANGUAGES:
            for month_num, month_name in MONTHS[lang].items():
                assert isinstance(month_name, str)
                assert len(month_name) > 0
