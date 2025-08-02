# app/modules/sales/api/v1/__init__.py
from app.modules.sales.api.v1.routes import router as sales_api_router

__all__ = ['sales_api_router']
