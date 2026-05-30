from fastapi import APIRouter, HTTPException
from ..scheduler import scheduler
from ..schema import ExecutorInfo

router = APIRouter(prefix="/api/executors", tags=["API - Executors"])

@router.get("/", response_model=list[ExecutorInfo])
def list_executors():
    return [
        ExecutorInfo.model_validate({"alias": alias, "executor": executor})
        for alias, executor in scheduler._executors.items()
    ]

@router.post("/", response_model=ExecutorInfo)
def create_executor(executor_info: ExecutorInfo):
    if executor_info.alias in scheduler._executors:
        raise HTTPException(status_code=400, detail=f"Executor '{executor_info.alias}' already exists")
    
    executor = executor_info.get_executor()
    scheduler.add_executor(executor, alias=executor_info.alias)
    return executor_info

@router.delete("/{alias}")
def delete_executor(alias: str):
    if alias not in scheduler._executors:
        raise HTTPException(status_code=404, detail=f"Executor '{alias}' not found")
    if alias == "default":
        raise HTTPException(status_code=400, detail="Cannot remove default executor")
    
    scheduler.remove_executor(alias)
    return {"status": "success", "alias": alias}