import pytest
from services.pdf_generator import PdfGeneratorService, pdf_generator_service


class TestPdfGeneratorService:
    def test_generate_pdf_classic_template(self):
        resume_data = {
            "personal_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "555-1234",
                "location": "New York, NY"
            },
            "summary": "Experienced software engineer",
            "work_experiences": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "description": "Built web applications",
                    "included": True
                }
            ],
            "skills": [
                {"name": "Python", "included": True},
                {"name": "JavaScript", "included": True}
            ],
            "education": [
                {
                    "degree": "BS",
                    "field_of_study": "Computer Science",
                    "institution": "MIT",
                    "graduation_year": "2019",
                    "included": True
                }
            ],
            "projects": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "classic")

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_modern_template(self):
        resume_data = {
            "personal_info": {
                "full_name": "Jane Smith",
                "email": "jane@example.com"
            },
            "summary": "Product manager with 5 years experience",
            "work_experiences": [
                {
                    "title": "Product Manager",
                    "company": "StartupXYZ",
                    "start_date": "2021-01",
                    "end_date": None,
                    "description": "Led product development",
                    "included": True
                }
            ],
            "skills": [
                {"name": "Agile", "included": True}
            ],
            "education": [],
            "projects": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "modern")

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_invalid_template(self):
        resume_data = {"personal_info": {"full_name": "Test"}}

        with pytest.raises(ValueError) as exc_info:
            pdf_generator_service.generate_pdf(resume_data, "invalid_template")

        assert "Invalid template" in str(exc_info.value)

    def test_section_filtering_included_only(self):
        resume_data = {
            "personal_info": {"full_name": "Test User", "email": "test@test.com"},
            "work_experiences": [
                {"title": "Job 1", "company": "A", "included": True},
                {"title": "Job 2", "company": "B", "included": False},
                {"title": "Job 3", "company": "C", "included": True}
            ],
            "skills": [
                {"name": "Skill1", "included": True},
                {"name": "Skill2", "included": False}
            ],
            "education": [
                {"degree": "BS", "institution": "Uni", "included": True},
                {"degree": "MS", "institution": "Uni2", "included": False}
            ],
            "projects": [
                {"name": "Proj1", "included": True},
                {"name": "Proj2", "included": False}
            ]
        }

        context = pdf_generator_service._prepare_context(resume_data)

        assert len(context["work_experiences"]) == 2
        assert context["work_experiences"][0]["title"] == "Job 1"
        assert context["work_experiences"][1]["title"] == "Job 3"

        assert len(context["skills"]) == 1
        assert context["skills"][0]["name"] == "Skill1"

        assert len(context["education"]) == 1
        assert context["education"][0]["degree"] == "BS"

        assert len(context["projects"]) == 1
        assert context["projects"][0]["name"] == "Proj1"

    def test_projects_default_to_excluded(self):
        resume_data = {
            "personal_info": {"full_name": "Test"},
            "projects": [
                {"name": "Project Without Included Field"},
                {"name": "Included Project", "included": True}
            ]
        }

        context = pdf_generator_service._prepare_context(resume_data)

        assert len(context["projects"]) == 1
        assert context["projects"][0]["name"] == "Included Project"

    def test_work_default_to_included(self):
        resume_data = {
            "personal_info": {"full_name": "Test"},
            "work_experiences": [
                {"title": "Job Without Included Field", "company": "A"},
                {"title": "Excluded Job", "company": "B", "included": False}
            ]
        }

        context = pdf_generator_service._prepare_context(resume_data)

        assert len(context["work_experiences"]) == 1
        assert context["work_experiences"][0]["title"] == "Job Without Included Field"

    def test_empty_sections_handling(self):
        resume_data = {
            "personal_info": {"full_name": "Test"},
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "classic")

        assert pdf_bytes is not None
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_brussels_template(self):
        """Test Brussels template generates valid PDF with two-column layout."""
        resume_data = {
            "personal_info": {
                "full_name": "Marie Dupont",
                "email": "marie@example.be",
                "phone": "+32 123 456 789",
                "location": "Brussels, Belgium"
            },
            "summary": "Experienced EU policy analyst",
            "work_experiences": [
                {
                    "title": "Policy Analyst",
                    "company": "European Commission",
                    "start_date": "2019-01",
                    "end_date": None,
                    "description": "Led policy research",
                    "included": True
                }
            ],
            "skills": [
                {"name": "Policy Analysis", "included": True},
                {"name": "EU Law", "included": True}
            ],
            "education": [
                {
                    "degree": "MA",
                    "field_of_study": "European Studies",
                    "institution": "College of Europe",
                    "graduation_year": "2018",
                    "included": True
                }
            ],
            "languages": [
                {"name": "French", "level": "Native", "included": True},
                {"name": "English", "level": "C2", "included": True}
            ],
            "projects": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "brussels")

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_eu_classic_template(self):
        """Test EU Classic template generates valid PDF with header photo area."""
        resume_data = {
            "personal_info": {
                "full_name": "Hans Mueller",
                "email": "hans@example.de",
                "phone": "+49 123 456789",
                "location": "Berlin, Germany"
            },
            "summary": "Senior software engineer with 10 years experience",
            "work_experiences": [
                {
                    "title": "Senior Engineer",
                    "company": "SAP",
                    "start_date": "2018-03",
                    "end_date": "2023-12",
                    "description": "Led backend development",
                    "included": True
                }
            ],
            "skills": [
                {"name": "Java", "included": True},
                {"name": "Kubernetes", "included": True}
            ],
            "education": [
                {
                    "degree": "Diplom-Informatiker",
                    "field_of_study": "Computer Science",
                    "institution": "TU Munich",
                    "graduation_year": "2014",
                    "included": True
                }
            ],
            "languages": [
                {"name": "German", "level": "Native", "included": True},
                {"name": "English", "level": "C1", "included": True}
            ],
            "projects": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "eu_classic")

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_photo(self):
        """Test PDF generation with base64 photo data."""
        # Small 1x1 pixel PNG as base64
        tiny_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        resume_data = {
            "personal_info": {
                "full_name": "Photo Test",
                "email": "photo@test.com",
                "photo": tiny_png
            },
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
            "languages": []
        }

        pdf_bytes = pdf_generator_service.generate_pdf(resume_data, "brussels")

        assert pdf_bytes is not None
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_without_photo_shows_placeholder(self):
        """Test PDF generation without photo uses placeholder."""
        resume_data = {
            "personal_info": {
                "full_name": "No Photo Test",
                "email": "nophoto@test.com"
            },
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
            "languages": []
        }

        # Both European templates should work without photo
        pdf_brussels = pdf_generator_service.generate_pdf(resume_data, "brussels")
        pdf_eu_classic = pdf_generator_service.generate_pdf(resume_data, "eu_classic")

        assert pdf_brussels is not None
        assert pdf_brussels[:4] == b"%PDF"
        assert pdf_eu_classic is not None
        assert pdf_eu_classic[:4] == b"%PDF"

    def test_languages_context_included(self):
        """Test that languages are properly included in context."""
        resume_data = {
            "personal_info": {"full_name": "Test"},
            "languages": [
                {"name": "English", "level": "Native", "included": True},
                {"name": "French", "level": "B2", "included": False},
                {"name": "German", "level": "A1", "included": True}
            ]
        }

        context = pdf_generator_service._prepare_context(resume_data)

        assert len(context["languages"]) == 2
        assert context["languages"][0]["name"] == "English"
        assert context["languages"][1]["name"] == "German"


class TestFilenameGeneration:
    def test_filename_with_spaces(self):
        resume_data = {"personal_info": {"full_name": "John Doe"}}
        company = "Tech Company"

        filename = pdf_generator_service.generate_filename(resume_data, company)

        assert filename == "John_Doe_Resume_Tech_Company.pdf"

    def test_filename_with_special_characters(self):
        resume_data = {"personal_info": {"full_name": "José García"}}
        company = "Café & Co."

        filename = pdf_generator_service.generate_filename(resume_data, company)

        assert filename == "Jos_Garca_Resume_Caf__Co.pdf"

    def test_filename_with_none_company(self):
        resume_data = {"personal_info": {"full_name": "Test User"}}

        filename = pdf_generator_service.generate_filename(resume_data, None)

        assert filename == "Test_User_Resume_Company.pdf"

    def test_filename_with_missing_name(self):
        resume_data = {"personal_info": {}}
        company = "TestCo"

        filename = pdf_generator_service.generate_filename(resume_data, company)

        assert filename == "Resume_Resume_TestCo.pdf"

    def test_filename_with_empty_personal_info(self):
        resume_data = {}
        company = "TestCo"

        filename = pdf_generator_service.generate_filename(resume_data, company)

        assert filename == "Resume_Resume_TestCo.pdf"
