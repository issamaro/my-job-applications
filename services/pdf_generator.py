# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Generate PDF resumes from HTML templates using Playwright Chromium.

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from services.translations import load_translations, format_date


PAGE_SETTINGS = {
    "classic":    {"format": "Letter", "margin": {"top": "0.75in", "right": "0.75in", "bottom": "0.75in", "left": "0.75in"}},
    "modern":     {"format": "Letter", "margin": {"top": "0.75in", "right": "0.75in", "bottom": "0.75in", "left": "0.75in"}},
    "brussels":   {"format": "A4", "margin": {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}},
    "eu_classic": {"format": "A4", "margin": {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}},
}


class PdfGeneratorService:
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    VALID_TEMPLATES = ["classic", "modern", "brussels", "eu_classic"]

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=select_autoescape(["html"])
        )

    def generate_pdf(self, resume_data: dict, template: str = "classic", language: str = "en") -> bytes:
        if template not in self.VALID_TEMPLATES:
            raise ValueError(f"Invalid template: {template}")

        html_template = self.env.get_template(f"resume_{template}.html")
        html_content = html_template.render(**self._prepare_context(resume_data, language))

        css_content = (self.TEMPLATES_DIR / "resume_base.css").read_text()
        html_with_style = html_content.replace("</head>", f"<style>{css_content}</style></head>")

        settings = PAGE_SETTINGS[template]

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.set_content(html_with_style, wait_until="load")
            pdf_bytes = page.pdf(
                format=settings["format"],
                margin=settings["margin"],
                print_background=True,
            )
            browser.close()

        return pdf_bytes

    def _prepare_context(self, resume_data: dict, language: str = "en") -> dict:
        translations = load_translations(language)

        work_experiences = []
        for exp in resume_data.get("work_experiences", []):
            if exp.get("included", True):
                formatted_exp = dict(exp)
                formatted_exp["formatted_start_date"] = format_date(exp.get("start_date"), language)
                formatted_exp["formatted_end_date"] = format_date(exp.get("end_date"), language)
                work_experiences.append(formatted_exp)

        return {
            "personal_info": resume_data.get("personal_info", {}),
            "summary": resume_data.get("summary"),
            "work_experiences": work_experiences,
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
            "languages": [
                lang for lang in resume_data.get("languages", [])
                if lang.get("included", True)
            ],
            "labels": translations,
            "language": language,
        }

    def generate_filename(self, resume_data: dict, company_name: str | None) -> str:
        name = resume_data.get("personal_info", {}).get("full_name", "Resume")
        company = company_name or "Company"

        name = name.replace(" ", "_")
        company = company.replace(" ", "_")
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        name = "".join(c for c in name if c in safe_chars)
        company = "".join(c for c in company if c in safe_chars)

        return f"{name}_Resume_{company}.pdf"


pdf_generator_service = PdfGeneratorService()
