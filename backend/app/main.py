from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.erp import router as erp_router
from app.api.logistics import router as logistics_router
from app.api.procurement import router as procurement_router
from app.api.workflows import router as workflows_router

app = FastAPI(
    title="Supply Chain Exception Agent API",
    version="1.0.0",
    description="API for Supply Chain Exception Monitoring and Automated Workflows"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(erp_router)
app.include_router(procurement_router)
app.include_router(logistics_router)
app.include_router(workflows_router)
app.include_router(dashboard_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

