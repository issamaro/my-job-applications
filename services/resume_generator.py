import json
from database import get_db
from services.profile import profile_service
from services.llm import llm_service
from services.job_descriptions import job_description_service
from schemas import (
    GeneratedResumeResponse,
    JobAnalysis,
    ResumeContent,
    ResumeWorkExperience,
    ResumeSkill,
    ResumeEducation,
    ResumeProject,
    ResumeLanguage,
)


class ProfileIncompleteError(Exception):
    pass


class ResumeGeneratorService:
    async def generate(self, job_description: str, job_description_id: int | None = None, language: str = "en") -> GeneratedResumeResponse:
        if not profile_service.has_work_experience():
            raise ProfileIncompleteError(
                "Your profile needs work experience before you can generate a tailored resume."
            )

        profile = profile_service.get_complete()
        profile_dict = profile.model_dump()

        # Save photo before removing it (we'll restore it later)
        saved_photo = None
        if profile_dict.get("personal_info") and "photo" in profile_dict["personal_info"]:
            saved_photo = profile_dict["personal_info"]["photo"]
            # Remove photo from profile to avoid sending huge base64 data to LLM
            del profile_dict["personal_info"]["photo"]

        llm_result = await llm_service.analyze_and_generate(job_description, profile_dict, language)

        # Restore photo to profile_dict for use in resume
        if saved_photo and profile_dict.get("personal_info"):
            profile_dict["personal_info"]["photo"] = saved_photo

        # Build title from LLM result
        job_title = llm_result.get("job_title", "Untitled")
        company_name = llm_result.get("company_name", "Unknown Company")
        title = f"{job_title} at {company_name}"

        # Save job analysis via service (single source of truth for JD mutations)
        jd_id = job_description_service.save_job_analysis(
            job_analysis=llm_result.get("job_analysis", {}),
            title=title,
            company_name=company_name,
            raw_text=job_description if not job_description_id else None,
            jd_id=job_description_id,
        )

        with get_db() as conn:
            resume_content = llm_result.get("resume", {})
            if profile_dict.get("personal_info"):
                resume_content["personal_info"] = profile_dict["personal_info"]

            # Include languages from profile (all languages are included by default)
            if profile_dict.get("languages"):
                resume_content["languages"] = [
                    {"id": lang["id"], "name": lang["name"], "level": lang["level"], "included": True}
                    for lang in profile_dict["languages"]
                ]

            # Store job_analysis directly in resume record (isolation per resume)
            job_analysis = llm_result.get("job_analysis")
            job_analysis_json = json.dumps(job_analysis) if job_analysis else None

            cursor = conn.execute(
                """
                INSERT INTO generated_resumes
                (job_description_id, job_title, company_name, match_score, resume_content, language, job_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    jd_id,
                    llm_result.get("job_title"),
                    llm_result.get("company_name"),
                    llm_result.get("match_score"),
                    json.dumps(resume_content),
                    language,
                    job_analysis_json,
                ),
            )
            conn.commit()
            resume_id = cursor.lastrowid

            cursor = conn.execute(
                "SELECT * FROM generated_resumes WHERE id = ?", (resume_id,)
            )
            row = cursor.fetchone()

            return self._row_to_response(dict(row))

    def get_resume(self, resume_id: int) -> GeneratedResumeResponse | None:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM generated_resumes WHERE id = ?",
                (resume_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_response(dict(row))

    def get_history(self) -> list[dict]:
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT id, job_title, company_name, match_score, created_at
                FROM generated_resumes
                ORDER BY created_at DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_resume(
        self, resume_id: int, resume_content: ResumeContent
    ) -> GeneratedResumeResponse | None:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT id FROM generated_resumes WHERE id = ?", (resume_id,)
            )
            if cursor.fetchone() is None:
                return None

            cursor = conn.execute(
                "SELECT resume_content FROM generated_resumes WHERE id = ?", (resume_id,)
            )
            existing = cursor.fetchone()
            existing_content = json.loads(existing["resume_content"]) if existing else {}

            new_content = resume_content.model_dump()
            if existing_content.get("personal_info"):
                new_content["personal_info"] = existing_content["personal_info"]

            conn.execute(
                """
                UPDATE generated_resumes
                SET resume_content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(new_content), resume_id),
            )
            conn.commit()

            return self.get_resume(resume_id)

    def delete_resume(self, resume_id: int) -> bool:
        with get_db() as conn:
            # Only delete the resume, NOT the JD
            # JD may have other resumes linked or user may want to keep it
            cursor = conn.execute(
                "DELETE FROM generated_resumes WHERE id = ?",
                (resume_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_response(self, row: dict) -> GeneratedResumeResponse:
        resume_content = json.loads(row["resume_content"]) if row.get("resume_content") else {}

        # Ensure photo from current profile is included (for European templates)
        personal_info = resume_content.get("personal_info", {})
        if personal_info and not personal_info.get("photo"):
            # Fetch current photo from profile
            profile = profile_service.get_complete()
            if profile.personal_info and profile.personal_info.get("photo"):
                personal_info["photo"] = profile.personal_info["photo"]
                resume_content["personal_info"] = personal_info

        work_experiences = [
            ResumeWorkExperience(**we) for we in resume_content.get("work_experiences", [])
        ]
        skills = [ResumeSkill(**s) for s in resume_content.get("skills", [])]
        education = [ResumeEducation(**e) for e in resume_content.get("education", [])]
        projects = [ResumeProject(**p) for p in resume_content.get("projects", [])]
        languages = [ResumeLanguage(**lang) for lang in resume_content.get("languages", [])]

        resume = ResumeContent(
            personal_info=resume_content.get("personal_info"),
            summary=resume_content.get("summary"),
            work_experiences=work_experiences,
            skills=skills,
            education=education,
            projects=projects,
            languages=languages,
        )

        # Read job_analysis directly from resume record (isolation per resume)
        job_analysis_obj = None
        if row.get("job_analysis"):
            job_analysis_data = json.loads(row["job_analysis"])
            job_analysis_obj = JobAnalysis(**job_analysis_data)

        return GeneratedResumeResponse(
            id=row["id"],
            job_title=row.get("job_title"),
            company_name=row.get("company_name"),
            match_score=row.get("match_score"),
            job_analysis=job_analysis_obj,
            resume=resume,
            language=row.get("language", "en"),
            created_at=row.get("created_at"),
        )


resume_generator_service = ResumeGeneratorService()
