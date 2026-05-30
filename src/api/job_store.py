from fastapi import APIRouter, HTTPException
from ..scheduler import scheduler
from ..schema import JobStoreInfo

router = APIRouter(prefix="/api/stores", tags=["API - Job Stores"])

@router.get("/", response_model=list[JobStoreInfo])
def list_stores():
    return [
        JobStoreInfo.model_validate({"alias": alias, "store": store})
        for alias, store in scheduler._jobstores.items()
    ]

@router.post("/", response_model=JobStoreInfo)
def create_store(store_info: JobStoreInfo):
    if store_info.alias in scheduler._jobstores:
        raise HTTPException(status_code=400, detail=f"Store '{store_info.alias}' already exists")
    
    store = store_info.get_store()
    scheduler.add_jobstore(store, alias=store_info.alias)
    return store_info

@router.delete("/{alias}")
def delete_store(alias: str):
    if alias not in scheduler._jobstores:
        raise HTTPException(status_code=404, detail=f"Store '{alias}' not found")
    if alias == "default":
        raise HTTPException(status_code=400, detail="Cannot remove default store")
    
    scheduler.remove_jobstore(alias)
    return {"status": "success", "alias": alias}