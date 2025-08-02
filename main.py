from fastapi import FastAPI
from app.modules.sales.api.v1.routes import router as module_router

app = FastAPI(title="Bheem Sales Module")
app.include_router(module_router, prefix="/api/sales")