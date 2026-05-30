import re
from typing import Literal
from fastapi import APIRouter, HTTPException

from ..config import LOG_PATH
from ..log import PARSE_PATTERN
from ..log import server_log as logger

router = APIRouter(prefix="/api/logs", tags=["API - Logs"])

def get_available_files(kind: str) -> list[str]:
    """Helper: Get log filenames based on kind."""
    if kind == "scheduler":
        return [f.name for f in sorted(LOG_PATH.glob("scheduler*log"))]
    else:
        # All logs that are NOT scheduler logs
        return [
            f.name for f in sorted(LOG_PATH.glob("*.log"), reverse=True)
            if not re.match(r"scheduler(\.[\d_-]+)?\.log", f.name)
        ]

@router.get("/{kind}/files", response_model=list[str])
def list_log_files(kind: Literal["jobs", "scheduler"]):
    """SDK Endpoint: Get available log files for a specific category."""
    return get_available_files(kind)

@router.get("/{kind}/content")
def get_log_content(
    kind: Literal["jobs", "scheduler"],
    log_file: str | None = None,
    level: str = "",
    module: str = "",
    page: int = 1,
    page_size: int = 1000
):
    """SDK Endpoint: Fetch parsed log entries as structured JSON."""
    files = get_available_files(kind)
    if not files:
        return {"logs": [], "total": 0, "page": page}
        
    log_file = log_file or (files[0] if files else None)
    if not log_file:
        return {"logs": [], "total": 0, "page": page}
    target_path = LOG_PATH / log_file

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")

    parsed_logs = []
    # Parse physical log lines into dictionary objects
    for line in logger.parse(target_path, pattern=PARSE_PATTERN):
        if level and line["level"] != level:
            continue
        if module and module not in line["name"]:
            continue
        parsed_logs.append(line)

    # Calculate pagination slice
    start = (page - 1) * page_size
    end = page * page_size
    
    return {
        "file": log_file,
        "total": len(parsed_logs),
        "page": page,
        "page_size": page_size,
        "logs": parsed_logs[start:end]
    } 