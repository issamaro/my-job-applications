from fastapi import APIRouter, HTTPException
from schemas import (
    JobCreate,
    JobUpdate,
    JobListItem,
    JobResponse,
    JobVersion,
    ResumeHistoryItem,
)
from services.jobs import job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobListItem])
async def list_jobs():
    """List all saved jobs with preview and resume count"""
    jobs = job_service.list_all()
    return [JobListItem.model_validate(job) for job in jobs]


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(request: JobCreate):
    """Save new job independently"""
    job = job_service.create(request.original_text)
    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """Get single job"""
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, request: JobUpdate):
    """Update job title or text"""
    data = request.model_dump(exclude_unset=True)
    job = job_service.update(job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int):
    """Delete job and linked resumes"""
    deleted = job_service.delete(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return None


@router.get("/{job_id}/resumes", response_model=list[ResumeHistoryItem])
async def get_job_resumes(job_id: int):
    """Get resumes linked to job"""
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resumes = job_service.get_resumes(job_id)
    return [ResumeHistoryItem.model_validate(r) for r in resumes]


@router.get("/{job_id}/versions", response_model=list[JobVersion])
async def get_job_versions(job_id: int):
    """Get version history"""
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    versions = job_service.get_versions(job_id)
    return [JobVersion.model_validate(v) for v in versions]


@router.post("/{job_id}/versions/{version_id}/restore", response_model=JobResponse)
async def restore_job_version(job_id: int, version_id: int):
    """Restore previous version"""
    job = job_service.restore_version(job_id, version_id)
    if not job:
        raise HTTPException(status_code=404, detail="Version not found")
    return JobResponse.model_validate(job)
