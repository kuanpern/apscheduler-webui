from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from ..scheduler import scheduler
from ..schema import JobStoreInfo

router = APIRouter(tags=["UI - Job Stores"])
templates = Jinja2Templates(directory="templates")

@router.get("/store", response_class=HTMLResponse)
async def stores_page(request: Request):
    stores = [
        JobStoreInfo.model_validate({"alias": alias, "store": store})
        for alias, store in scheduler._jobstores.items()
    ]
    return templates.TemplateResponse(
        request=request, name="stores.html", context={"stores": stores}
    )

@router.post("/ui/store/new")
async def ui_create_store(request: Request):
    form_data = await request.form()
    data_dict = dict(form_data)
    
    try:
        store_info = JobStoreInfo(**data_dict)
        if store_info.alias in scheduler._jobstores:
            return HTMLResponse(f"<div class='alert alert-danger'>Store '{store_info.alias}' already exists</div>", status_code=400)
        
        scheduler.add_jobstore(store_info.get_store(), alias=store_info.alias)
    except ValidationError as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Validation Error: {e.errors()}</div>", status_code=400)
    except Exception as e:
        return HTMLResponse(f"<div class='alert alert-danger'>Error: {str(e)}</div>", status_code=400)
        
    return Response(headers={"HX-Refresh": "true"})

@router.post("/ui/store/{alias}/remove")
async def ui_remove_store(alias: str):
    if alias not in scheduler._jobstores:
        raise HTTPException(status_code=404, detail="Store not found")
    if alias == "default":
        raise HTTPException(status_code=400, detail="Cannot remove default store")
        
    scheduler.remove_jobstore(alias)
    return Response(headers={"HX-Refresh": "true"})