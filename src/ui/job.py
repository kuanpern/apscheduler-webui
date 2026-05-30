from typing import Literal
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from ..scheduler import scheduler
from ..schema import JobInfo, NewJobParam
from ..api.job import create_job, job_action

router = APIRouter(tags=["UI - Jobs"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def jobs_page(request: Request):
    """Render the main jobs dashboard"""
    jobs = scheduler.get_jobs()
    job_models = [JobInfo.model_validate(job) for job in jobs]
    
    # Get available executors and stores for the form dropdowns
    executors = list(scheduler._executors.keys())
    jobstores = list(scheduler._jobstores.keys())
    
    return templates.TemplateResponse(
        request=request, 
        name="jobs.html", 
        context={
            "jobs": job_models,
            "executors": executors,
            "jobstores": jobstores
        }
    )

@router.post("/ui/job/new")
async def ui_create_job(request: Request):
    """Handle HTMX form submission for a new job"""
    form_data = await request.form()
    
    # Convert form data to a mutable dictionary
    job_dict = dict(form_data)
    
    # If ID is empty, remove it so Pydantic default_factory can kick in
    if not job_dict.get("id"):
        job_dict.pop("id", None)
    
    # HTML checkboxes don't send a value if unchecked. If checked, they send "on".
    job_dict["coalesce"] = "on" if job_dict.get("coalesce") == "on" else "off"
    
    try:
        # Let our existing schema validate and parse the flat form data
        job_param = NewJobParam(**job_dict)
        # Reuse the core SDK API logic!
        create_job(job_param)
    except ValidationError as e:
        # For now, return a raw error to the frontend.
        return HTMLResponse(f"<div class='alert alert-danger'>Validation Error: {e.errors()}</div>", status_code=400)
    except Exception as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Error: {str(e)}</div>", status_code=400)

    return Response(headers={"HX-Refresh": "true"})

@router.post("/ui/job/{id}/{action}")
async def ui_job_action(id: str, action: Literal["pause", "resume", "reload", "remove"]):
    """Handle HTMX button clicks and tell the browser to reload the page."""
    try:
        # Reuse the core logic from the API router to ensure consistency and safety checks
        job_action(id, action)
    except Exception as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Error: {str(e)}</div>", status_code=400)

    # HX-Refresh tells HTMX to do a full page reload instantly
    return Response(headers={"HX-Refresh": "true"})