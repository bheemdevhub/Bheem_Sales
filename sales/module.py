"""Sales module implementation"""

from typing import Dict, Any, List
from fastapi import APIRouter
from app.core.base_module import BaseERPModule


class SalesModule(BaseERPModule):
    """Sales module for managing sales operations"""
    
    def __init__(self, *args, **kwargs):
        self.module_name = "sales"
        self.version_number = "1.0.0"
        self.description = "Sales Management Module for Revenue Generation"
        super().__init__(*args, **kwargs)
        self._logger.info("Sales module created")

    @property
    def name(self) -> str:
        """Module name"""
        return self.module_name

    @property 
    def version(self) -> str:
        """Module version"""
        return self.version_number

    @property
    def permissions(self) -> List[str]:
        """List of permissions this module provides"""
        return [
            # General sales permissions
            "sales:read",
            "sales:write", 
            "sales:delete",
            "sales:admin",
            
            # Core sales process permissions
            "quotes:read",
            "quotes:write",
            "orders:read", 
            "orders:write",
            "invoices:read",
            "invoices:write",
            "customers:read",
            "customers:write",
            
            # SKU management permissions
            "sku.read",
            "sku.create",
            "sku.update",
            "sku.delete",
            
            # SKU pricing tier permissions
            "sku.pricing_tier.read",
            "sku.pricing_tier.create",
            "sku.pricing_tier.update",
            "sku.pricing_tier.delete",
            "sku.pricing_tier.calculate",
            
            # SKU variant permissions
            "sku.variant.read",
            "sku.variant.create",
            "sku.variant.update",
            "sku.variant.delete",
            
            # SKU bundle permissions
            "sku.bundle.read",
            "sku.bundle.create",
            "sku.bundle.update",
            "sku.bundle.delete",
            
            # Course management permissions
            "course.read",
            "course.create",
            "course.update",
            "course.delete",
            "course.publish",
            "course.enroll",
            
            # ERP Solution permissions
            "erp_solution.read",
            "erp_solution.create",
            "erp_solution.update",
            "erp_solution.delete",
            "erp_solution.configure",
            "erp_solution.deploy",
            
            # AI Agent permissions
            "ai_agent.read",
            "ai_agent.create",
            "ai_agent.update",
            "ai_agent.delete",
            "ai_agent.train",
            "ai_agent.deploy",
            
            # Physical Product permissions
            "physical_product.read",
            "physical_product.create",
            "physical_product.update",
            "physical_product.delete",
            "physical_product.inventory",
            "physical_product.shipping",
            
            # Sales module specific permissions
            "sales.quotes.create",
            "sales.quotes.read",
            "sales.quotes.update",
            "sales.quotes.delete",
            
            "sales.vendors.create",
            "sales.vendors.read",
            "sales.vendors.update",
            "sales.vendors.delete",
            
            "sales.bulk.import",
            "sales.bulk.export",
            "sales.bulk.update",
            
            "sales.analytics.dashboard",
            "sales.analytics.forecasts",
            "sales.analytics.performance",
            "sales.analytics.reporting",
            
            "sales.dashboard.executive",
            "sales.dashboard.manager",
            "sales.dashboard.rep",
            
            "sales.forecasting.read",
            "sales.territory.read",
            "sales.intelligence.read",
            "sales.collaboration.create",
            "sales.collaboration.read",
            "sales.gamification.read",
            "sales.coaching.read",
            "sales.optimization.create"
        ]

    def get_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": "active",
            "routes_count": len(self.router.routes) if hasattr(self, '_router') else 0
        }

    def _setup_routes(self):
        """Setup module routes"""
        # Call parent to get health check route
        super()._setup_routes()
        
        try:
            # Import main sales router that includes all routes
            from .api.v1.routes import router as sales_main_router
            
            # Include the main sales router
            # Include the main sales router WITHOUT extra prefix (so /api/sales/...)
            self._router.include_router(sales_main_router)
            # Add additional module-specific routes
            @self._router.get("/info")
            async def module_info():
                return self.get_info()
                
            @self._router.get("/permissions")
            async def module_permissions():
                return {
                    "module": self.name,
                    "permissions": self.permissions,
                    "total": len(self.permissions)
                }
                
            @self._router.get("/stats")
            async def module_stats():
                return {
                    "module": self.name,
                    "version": self.version,
                    "routes": len(self._router.routes),
                    "permissions": len(self.permissions),
                    "status": "active"
                }
                
        except ImportError as e:
            self._logger.error(f"Could not import sales routes: {e}")
            # Fallback to individual route imports
            self._setup_fallback_routes()

    def _setup_fallback_routes(self):
        """Fallback route setup if main router import fails"""
        self._logger.warning("Setting up fallback routes for sales module")
        
        @self._router.get("/status")
        async def fallback_status():
            return {
                "module": self.name,
                "status": "fallback_mode",
                "message": "Some routes may not be available"
            }

    async def _subscribe_to_events(self) -> None:
        """Subscribe to events from other modules"""
        if self._event_bus:
            # Listen for system events
            await self._event_bus.subscribe("system.company_created", self._handle_company_created)
            
            # Listen for events from other modules
            await self._event_bus.subscribe("inventory.product_stock_low", self._handle_product_stock_low)
            await self._event_bus.subscribe("accounting.invoice_paid", self._handle_invoice_paid)
            
    async def _handle_company_created(self, event):
        """Handle company creation event"""
        self._logger.info(f"New company created, initializing sales data: {event.get('company_id')}")
        # Logic to set up initial sales data for new company
        
    async def _handle_product_stock_low(self, event):
        """Handle low stock notification"""
        self._logger.info(f"Product stock low notification: {event.get('product_id')}")
        # Logic to handle low stock notifications
        
    async def _handle_invoice_paid(self, event):
        """Handle invoice payment notification"""
        self._logger.info(f"Invoice payment notification: {event.get('invoice_id')}")
        # Logic to handle paid invoice events

    async def initialize(self):
        """Initialize the sales module"""
        await super().initialize()
        await self._subscribe_to_events()
        self._logger.info(f"Sales module initialized with {len(self.permissions)} permissions")

    async def shutdown(self) -> None:
        """Shutdown sales module"""
        self._logger.info("Shutting down Sales Module")
        # Cleanup resources, close connections, etc.
        await super().shutdown()

    def get_models(self):
        """Get module models"""
        try:
            from .core.models import sku_models
            from app.shared.models import SKU
            return {
                "sku_models": sku_models,
                "base_sku": SKU
            }
        except ImportError as e:
            self._logger.error(f"Failed to import sales models: {e}")
            return None

    def get_available_endpoints(self):
        """Get list of available endpoints in this module"""
        endpoints = []
        for route in self._router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                endpoints.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', 'unnamed')
                })
        return endpoints
    
    def __init__(self, *args, **kwargs):
        self._module_name = "sales"
        self._version = "1.0.0"
        self.description = "Sales Management Module for Revenue Generation"
        super().__init__(*args, **kwargs)
        self._logger.info("Sales module created")

    @property
    def name(self) -> str:
        return self._module_name

    @property
    def version(self) -> str:
        return self._version

    @property
    def permissions(self) -> List[str]:
        # You can expand this list as needed
        return [
            "sales:read", "sales:write", "sales:delete", "sales:admin",
            "quotes:read", "quotes:write",
            "orders:read", "orders:write",
            "invoices:read", "invoices:write",
            "customers:read", "customers:write",
            # ... add all other permissions as needed ...
        ]

    def get_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": "active",
            "routes_count": len(self.router.routes) if hasattr(self, '_router') else 0
        }

    def _setup_routes(self):
        """Setup module routes"""
        # Call parent to get health check route
        super()._setup_routes()
        try:
            # Import main sales router that includes all routes
            from app.modules.sales.api.v1.routes import router as sales_main_router
            # Include the main sales router with prefix (so /api/sales/sales/...)
            self._router.include_router(sales_main_router, prefix="/sales")
            # Add additional module-specific info endpoints if needed
            @self._router.get("/info")
            async def module_info():
                return self.get_info()
            @self._router.get("/permissions")
            async def module_permissions():
                return {
                    "module": self.name,
                    "permissions": self.permissions,
                    "total": len(self.permissions)
                }
        except ImportError as e:
            self._logger.error(f"Could not import sales routes: {e}")
            self._setup_fallback_routes()

    def _setup_fallback_routes(self):
        """Fallback route setup if main router import fails"""
        self._logger.warning("Setting up fallback routes for sales module")
        @self._router.get("/status")
        async def status():
            return {"status": "Sales module fallback active"}

    # ...existing code for event subscriptions and handlers...



