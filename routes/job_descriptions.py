from fastapi import APIRouter, HTTPException
from schemas import (
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobDescriptionListItem,
    JobDescriptionResponse,
    JobDescriptionVersion,
    ResumeHistoryItem,
)
from services.job_descriptions import job_description_service

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])


@router.get("", response_model=list[JobDescriptionListItem])
async def list_job_descriptions():
    """List all saved JDs with preview and resume count"""
    jobs = job_description_service.list_all()
    return [JobDescriptionListItem.model_validate(job) for job in jobs]


@router.post("", response_model=JobDescriptionResponse, status_code=201)
async def create_job_description(request: JobDescriptionCreate):
    """Save new JD independently"""
    job = job_description_service.create(request.raw_text)
    return JobDescriptionResponse.model_validate(job)


@router.get("/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(jd_id: int):
    """Get single JD"""
    job = job_description_service.get(jd_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobDescriptionResponse.model_validate(job)


@router.put("/{jd_id}", response_model=JobDescriptionResponse)
async def update_job_description(jd_id: int, request: JobDescriptionUpdate):
    """Update JD title or text"""
    data = request.model_dump(exclude_unset=True)
    job = job_description_service.update(jd_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobDescriptionResponse.model_validate(job)


@router.delete("/{jd_id}", status_code=204)
async def delete_job_description(jd_id: int):
    """Delete JD and linked resumes"""
    deleted = job_description_service.delete(jd_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job description not found")
    return None


@router.get("/{jd_id}/resumes", response_model=list[ResumeHistoryItem])
async def get_job_description_resumes(jd_id: int):
    """Get resumes linked to JD"""
    job = job_description_service.get(jd_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    resumes = job_description_service.get_resumes(jd_id)
    return [ResumeHistoryItem.model_validate(r) for r in resumes]


@router.get("/{jd_id}/versions", response_model=list[JobDescriptionVersion])
async def get_job_description_versions(jd_id: int):
    """Get version history"""
    job = job_description_service.get(jd_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    versions = job_description_service.get_versions(jd_id)
    return [JobDescriptionVersion.model_validate(v) for v in versions]


@router.post("/{jd_id}/versions/{version_id}/restore", response_model=JobDescriptionResponse)
async def restore_job_description_version(jd_id: int, version_id: int):
    """Restore previous version"""
    job = job_description_service.restore_version(jd_id, version_id)
    if not job:
        raise HTTPException(status_code=404, detail="Version not found")
    return JobDescriptionResponse.model_validate(job)
