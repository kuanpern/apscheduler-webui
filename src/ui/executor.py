from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from ..scheduler import scheduler
from ..schema import ExecutorInfo

router = APIRouter(tags=["UI - Executors"])
templates = Jinja2Templates(directory="templates")

@router.get("/executor", response_class=HTMLResponse)
async def executors_page(request: Request):
    executors = [
        ExecutorInfo.model_validate({"alias": alias, "executor": executor})
        for alias, executor in scheduler._executors.items()
    ]
    return templates.TemplateResponse(
        request=request, name="executors.html", context={"executors": executors}
    )

@router.post("/ui/executor/new")
async def ui_create_executor(request: Request):
    form_data = await request.form()
    data_dict = dict(form_data)
    
    # Handle empty strings for optional int fields
    if not data_dict.get("max_worker"):
        data_dict.pop("max_worker", None)

    try:
        executor_info = ExecutorInfo(**data_dict)
        if executor_info.alias in scheduler._executors:
            return HTMLResponse(f"<div class='alert alert-danger'>Executor '{executor_info.alias}' already exists</div>", status_code=400)
        
        scheduler.add_executor(executor_info.get_executor(), alias=executor_info.alias)
    except ValidationError as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Validation Error: {e.errors()}</div>", status_code=400)
    except Exception as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Error: {str(e)}</div>", status_code=400)
        
    return Response(headers={"HX-Refresh": "true"})

@router.post("/ui/executor/{alias}/remove")
async def ui_remove_executor(alias: str):
    if alias not in scheduler._executors:
        raise HTTPException(status_code=404, detail="Executor not found")
    if alias == "default":
        raise HTTPException(status_code=400, detail="Cannot remove default executor")
        
    scheduler.remove_executor(alias)
    return Response(headers={"HX-Refresh": "true"})