from typing import Literal
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Import the core logic from our API module
from ..api.job_log import get_available_files, get_log_content
from ..log import server_log as logger

router = APIRouter(tags=["UI - Logs"])
templates = Jinja2Templates(directory="templates")

@router.get("/log/{kind}", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    kind: Literal["jobs", "scheduler"],
    log_file: str | None = None,
    level: str = "",
    module: str = "",
    page: int = 1
):
    # Fetch data using the same backend logic as the API
    available_files = get_available_files(kind)
    log_data = get_log_content(kind, log_file, level, module, page)
    
    # Extract known log levels from Loguru for the dropdown
    levels = list(logger._core.levels.keys())

    return templates.TemplateResponse(
        request=request, 
        name="logs.html", 
        context={
            "kind": kind,
            "available_files": available_files,
            "current_file": log_data.get("file", log_file),
            "logs": log_data.get("logs", []),
            "total_logs": log_data.get("total", 0),
            "page": page,
            "level": level,
            "module": module,
            "levels": levels
        }
    )