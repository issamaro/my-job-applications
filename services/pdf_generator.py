from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


class PdfGeneratorService:
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    VALID_TEMPLATES = ["classic", "modern"]

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=select_autoescape(["html"])
        )

    def generate_pdf(self, resume_data: dict, template: str = "classic") -> bytes:
        """Generate PDF from resume data using specified template."""
        from weasyprint import HTML, CSS

        if template not in self.VALID_TEMPLATES:
            raise ValueError(f"Invalid template: {template}")

        html_template = self.env.get_template(f"resume_{template}.html")
        css = CSS(filename=self.TEMPLATES_DIR / "resume_base.css")

        html_content = html_template.render(**self._prepare_context(resume_data))

        html_doc = HTML(string=html_content)
        return html_doc.write_pdf(stylesheets=[css])

    def _prepare_context(self, resume_data: dict) -> dict:
        """Filter to only included sections."""
        return {
            "personal_info": resume_data.get("personal_info", {}),
            "summary": resume_data.get("summary"),
            "work_experiences": [
                exp for exp in resume_data.get("work_experiences", [])
                if exp.get("included", True)
            ],
            "skills": [
                skill for skill in resume_data.get("skills", [])
                if skill.get("included", True)
            ],
            "education": [
                edu for edu in resume_data.get("education", [])
                if edu.get("included", True)
            ],
            "projects": [
                proj for proj in resume_data.get("projects", [])
                if proj.get("included", False)
            ],
        }

    def generate_filename(self, resume_data: dict, company_name: str | None) -> str:
        """Generate PDF filename: FullName_Resume_Company.pdf"""
        name = resume_data.get("personal_info", {}).get("full_name", "Resume")
        company = company_name or "Company"

        name = name.replace(" ", "_")
        company = company.replace(" ", "_")
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        name = "".join(c for c in name if c in safe_chars)
        company = "".join(c for c in company if c in safe_chars)

        return f"{name}_Resume_{company}.pdf"


pdf_generator_service = PdfGeneratorService()
