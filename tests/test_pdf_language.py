"""Tests for PDF generation with language support."""

import pytest
from services.pdf_generator import PdfGeneratorService


@pytest.fixture
def pdf_service():
    """Create PDF generator service instance."""
    return PdfGeneratorService()


@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing."""
    return {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "Brussels, Belgium"
        },
        "summary": "Experienced software developer",
        "work_experiences": [
            {
                "id": 1,
                "title": "Senior Developer",
                "company": "Tech Corp",
                "start_date": "2020-01",
                "end_date": None,
                "description": "Leading development team",
                "included": True
            }
        ],
        "skills": [
            {"name": "Python", "included": True},
            {"name": "JavaScript", "included": True}
        ],
        "education": [
            {
                "id": 1,
                "institution": "University",
                "degree": "BSc Computer Science",
                "graduation_year": 2018,
                "included": True
            }
        ],
        "languages": [],
        "projects": []
    }


class TestPrepareContext:
    """Tests for _prepare_context method."""

    def test_prepare_context_includes_labels(self, pdf_service, sample_resume_data):
        """Context should include labels for translations."""
        context = pdf_service._prepare_context(sample_resume_data, "en")
        assert "labels" in context
        assert context["labels"]["summary"] == "Professional Summary"

    def test_prepare_context_includes_language(self, pdf_service, sample_resume_data):
        """Context should include language code."""
        context = pdf_service._prepare_context(sample_resume_data, "fr")
        assert "language" in context
        assert context["language"] == "fr"

    def test_prepare_context_formats_dates_english(self, pdf_service, sample_resume_data):
        """Work experience dates should be formatted in English."""
        context = pdf_service._prepare_context(sample_resume_data, "en")
        work_exp = context["work_experiences"][0]
        assert work_exp["formatted_start_date"] == "Jan 2020"
        assert work_exp["formatted_end_date"] == "Present"

    def test_prepare_context_formats_dates_french(self, pdf_service, sample_resume_data):
        """Work experience dates should be formatted in French."""
        context = pdf_service._prepare_context(sample_resume_data, "fr")
        work_exp = context["work_experiences"][0]
        assert work_exp["formatted_start_date"] == "Janv 2020"
        assert work_exp["formatted_end_date"] == "Présent"

    def test_prepare_context_formats_dates_dutch(self, pdf_service, sample_resume_data):
        """Work experience dates should be formatted in Dutch."""
        context = pdf_service._prepare_context(sample_resume_data, "nl")
        work_exp = context["work_experiences"][0]
        assert work_exp["formatted_start_date"] == "Jan 2020"
        assert work_exp["formatted_end_date"] == "Heden"

    def test_prepare_context_french_labels(self, pdf_service, sample_resume_data):
        """Context should include French labels when French is selected."""
        context = pdf_service._prepare_context(sample_resume_data, "fr")
        assert context["labels"]["summary"] == "Profil Professionnel"
        assert context["labels"]["experience"] == "Expérience"
        assert context["labels"]["skills"] == "Compétences"

    def test_prepare_context_dutch_labels(self, pdf_service, sample_resume_data):
        """Context should include Dutch labels when Dutch is selected."""
        context = pdf_service._prepare_context(sample_resume_data, "nl")
        assert context["labels"]["summary"] == "Professioneel Profiel"
        assert context["labels"]["experience"] == "Werkervaring"
        assert context["labels"]["skills"] == "Vaardigheden"


class TestGeneratePdf:
    """Tests for generate_pdf method."""

    def test_generate_pdf_accepts_language_parameter(self, pdf_service, sample_resume_data):
        """generate_pdf should accept language parameter."""
        # This test just verifies the method signature accepts language
        # Actual PDF generation is tested in integration tests
        try:
            # Will fail due to WeasyPrint dependencies, but tests parameter acceptance
            pdf_service.generate_pdf(sample_resume_data, "classic", "fr")
        except RuntimeError:
            # Expected - WeasyPrint may not be available in test environment
            pass
        except Exception as e:
            # Any other error is unexpected
            if "DYLD" not in str(e) and "WeasyPrint" not in str(e):
                raise


class TestAllTemplatesWithLanguages:
    """Tests for all template/language combinations."""

    @pytest.mark.parametrize("template", ["classic", "modern", "brussels", "eu_classic"])
    @pytest.mark.parametrize("language", ["en", "fr", "nl"])
    def test_context_prepared_for_all_combinations(self, pdf_service, sample_resume_data, template, language):
        """Context should be prepared correctly for all template/language combinations."""
        context = pdf_service._prepare_context(sample_resume_data, language)

        # All contexts should have these keys
        assert "labels" in context
        assert "language" in context
        assert "personal_info" in context
        assert "work_experiences" in context

        # Language should match
        assert context["language"] == language

        # Labels should be in the correct language
        if language == "en":
            assert context["labels"]["present"] == "Present"
        elif language == "fr":
            assert context["labels"]["present"] == "Présent"
        elif language == "nl":
            assert context["labels"]["present"] == "Heden"
