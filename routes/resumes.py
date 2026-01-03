from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from schemas import (
    ResumeGenerateRequest,
    GeneratedResumeResponse,
    ResumeHistoryItem,
    ResumeUpdateRequest,
    CompleteProfile,
)
from services.resume_generator import resume_generator_service, ProfileIncompleteError
from services.profile import profile_service
from services.pdf_generator import pdf_generator_service

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/generate", response_model=GeneratedResumeResponse)
async def generate_resume(request: ResumeGenerateRequest):
    try:
        result = await resume_generator_service.generate(request.job_description)
        return result
    except ProfileIncompleteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ResumeHistoryItem])
async def list_resumes():
    history = resume_generator_service.get_history()
    return [ResumeHistoryItem.model_validate(item) for item in history]


@router.get("/{resume_id}", response_model=GeneratedResumeResponse)
async def get_resume(resume_id: int):
    resume = resume_generator_service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}", response_model=GeneratedResumeResponse)
async def update_resume(resume_id: int, request: ResumeUpdateRequest):
    resume = resume_generator_service.update_resume(resume_id, request.resume)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: int):
    deleted = resume_generator_service.delete_resume(resume_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")
    return None


@router.get("/{resume_id}/pdf")
async def export_resume_pdf(
    resume_id: int,
    template: str = Query(default="classic", pattern="^(classic|modern)$")
):
    resume = resume_generator_service.get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        pdf_bytes = pdf_generator_service.generate_pdf(
            resume.resume.model_dump() if resume.resume else {},
            template
        )
        filename = pdf_generator_service.generate_filename(
            resume.resume.model_dump() if resume.resume else {},
            resume.company_name
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Could not generate PDF")


profile_router = APIRouter(prefix="/api/profile", tags=["profile"])


@profile_router.get("/complete", response_model=CompleteProfile)
async def get_complete_profile():
    return profile_service.get_complete()
