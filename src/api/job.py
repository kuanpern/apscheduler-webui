import importlib
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, HTTPException

from ..scheduler import scheduler
from ..schema import JobInfo, NewJobParam
from ..exceptions import InvalidAction
from ..uv import uv_available, uv_run

router = APIRouter(prefix="/api/jobs", tags=["API - Jobs"])

@router.get("/", response_model=list[JobInfo])
def list_jobs():
    """SDK Endpoint: Get all scheduled jobs"""
    jobs = scheduler.get_jobs()
    return [JobInfo.model_validate(job) for job in jobs]

@router.get("/{id}", response_model=JobInfo)
def get_job(id: str):
    """SDK Endpoint: Get a specific job"""
    job = scheduler.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobInfo.model_validate(job)

@router.post("/", response_model=JobInfo)
def create_job(job_info: NewJobParam):
    """SDK Endpoint: Create a new job"""
    trigger = job_info.get_trigger()
    func = job_info.func
    args = job_info.args

    if func == "uv_run":
        if not uv_available:
            raise HTTPException(400, "uv is not available.")
        if not (script := job_info.uv_script) or not Path(script).exists():
            raise HTTPException(400, f"Script '{script}' does not exist")
        func = uv_run
        args = (script, *args)

    job = scheduler.add_job(
        func,
        trigger=trigger,
        args=args,
        kwargs=job_info.kwargs,
        coalesce=job_info.coalesce,
        max_instances=job_info.max_instances,
        misfire_grace_time=job_info.misfire_grace_time,
        name=job_info.name,
        id=job_info.id,
        executor=job_info.executor,
        jobstore=job_info.jobstore,
        replace_existing=True
    )
    return JobInfo.model_validate(job)

@router.post("/{id}/{action}")
def job_action(id: str, action: Literal["pause", "resume", "reload", "remove"]):
    """SDK Endpoint: Perform an action on a job"""
    job = scheduler.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    match action:
        case "pause":
            scheduler.pause_job(id)
        case "resume":
            scheduler.resume_job(id)
        case "remove":
            scheduler.remove_job(id)
        case "reload":
            if callable(job.func):
                module = importlib.import_module(job.func.__module__)
                importlib.reload(module)
            else:
                raise HTTPException(status_code=400, detail="Cannot reload string reference functions")
        case _:
            raise InvalidAction(action)
    
    return {"status": "success", "action": action, "job_id": id}