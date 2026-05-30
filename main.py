from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.scheduler import scheduler
from src.api.job import router as api_job_router
from src.ui.job import router as ui_job_router
from src.api.executor import router as api_executor_router
from src.ui.executor import router as ui_executor_router
from src.api.job_store import router as api_store_router
from src.ui.job_store import router as ui_store_router
from src.api.job_log import router as api_log_router
from src.ui.job_log import router as ui_log_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Mount the JSON API for the SDK
app.include_router(api_job_router)

# Mount the UI Views for HTMX
app.include_router(ui_job_router)
app.include_router(api_executor_router)
app.include_router(ui_executor_router)
app.include_router(api_store_router)
app.include_router(ui_store_router)
app.include_router(api_log_router)
app.include_router(ui_log_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
