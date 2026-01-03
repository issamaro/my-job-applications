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
