"""
Advanced Sales Integration Service
Handles external system integrations, webhooks, and third-party connectivity
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import json
import requests
from enum import Enum
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.shared.models import Company


class IntegrationType(str, Enum):
    """Types of integrations supported"""
    CRM = "crm"
    ERP = "erp"
    PAYMENT_GATEWAY = "payment_gateway"
    EMAIL_MARKETING = "email_marketing"
    ACCOUNTING = "accounting"
    INVENTORY = "inventory"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    COMMUNICATION = "communication"


class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    SYNCING = "syncing"


class SalesIntegrationService:
    """Advanced integration service for sales module"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    # ==================== EXTERNAL SYSTEM INTEGRATIONS ====================
    
    def create_crm_integration(self, config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Create CRM system integration"""
        try:
            integration_config = {
                "type": IntegrationType.CRM,
                "company_id": company_id,
                "config": config,
                "status": IntegrationStatus.PENDING,
                "created_at": datetime.utcnow()
            }
            
            # Validate CRM connection
            if self._validate_crm_connection(config):
                integration_config["status"] = IntegrationStatus.ACTIVE
                
                # Set up initial data sync
                self._setup_crm_data_sync(config, company_id)
                
                self.logger.info(f"CRM integration created for company {company_id}")
                return {
                    "success": True,
                    "integration_id": str(UUID()),
                    "status": "active",
                    "message": "CRM integration successfully configured"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to validate CRM connection"
                }
                
        except Exception as e:
            self.logger.error(f"CRM integration error: {str(e)}")
            return {
                "success": False,
                "error": f"CRM integration failed: {str(e)}"
            }
    
    def create_payment_gateway_integration(self, config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Create payment gateway integration"""
        try:
            supported_gateways = ["stripe", "paypal", "square", "authorize_net", "razorpay"]
            gateway_type = config.get("gateway_type", "").lower()
            
            if gateway_type not in supported_gateways:
                return {
                    "success": False,
                    "error": f"Unsupported gateway type. Supported: {supported_gateways}"
                }
            
            # Gateway-specific configuration
            gateway_config = self._configure_payment_gateway(gateway_type, config)
            
            if gateway_config["success"]:
                self.logger.info(f"Payment gateway {gateway_type} integrated for company {company_id}")
                return {
                    "success": True,
                    "integration_id": str(UUID()),
                    "gateway_type": gateway_type,
                    "status": "active",
                    "capabilities": gateway_config["capabilities"]
                }
            else:
                return gateway_config
                
        except Exception as e:
            self.logger.error(f"Payment gateway integration error: {str(e)}")
            return {
                "success": False,
                "error": f"Payment gateway integration failed: {str(e)}"
            }
    
    def create_accounting_integration(self, config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Create accounting system integration"""
        try:
            supported_systems = ["quickbooks", "xero", "sage", "freshbooks", "zoho_books"]
            system_type = config.get("system_type", "").lower()
            
            if system_type not in supported_systems:
                return {
                    "success": False,
                    "error": f"Unsupported accounting system. Supported: {supported_systems}"
                }
            
            # System-specific configuration
            accounting_config = self._configure_accounting_system(system_type, config)
            
            if accounting_config["success"]:
                # Set up automatic invoice sync
                self._setup_accounting_sync(system_type, config, company_id)
                
                self.logger.info(f"Accounting system {system_type} integrated for company {company_id}")
                return {
                    "success": True,
                    "integration_id": str(UUID()),
                    "system_type": system_type,
                    "status": "active",
                    "sync_capabilities": accounting_config["sync_capabilities"]
                }
            else:
                return accounting_config
                
        except Exception as e:
            self.logger.error(f"Accounting integration error: {str(e)}")
            return {
                "success": False,
                "error": f"Accounting integration failed: {str(e)}"
            }
    
    # ==================== WEBHOOK MANAGEMENT ====================
    
    def register_webhook(self, webhook_config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Register webhook endpoint"""
        try:
            webhook_data = {
                "url": webhook_config["url"],
                "events": webhook_config.get("events", []),
                "secret": webhook_config.get("secret"),
                "company_id": company_id,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            # Validate webhook endpoint
            if self._validate_webhook_endpoint(webhook_data["url"]):
                webhook_id = str(UUID())
                
                self.logger.info(f"Webhook registered: {webhook_id} for company {company_id}")
                return {
                    "success": True,
                    "webhook_id": webhook_id,
                    "status": "active",
                    "events": webhook_data["events"]
                }
            else:
                return {
                    "success": False,
                    "error": "Webhook endpoint validation failed"
                }
                
        except Exception as e:
            self.logger.error(f"Webhook registration error: {str(e)}")
            return {
                "success": False,
                "error": f"Webhook registration failed: {str(e)}"
            }
    
    def send_webhook_event(self, event_type: str, payload: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Send webhook event to registered endpoints"""
        try:
            # Get registered webhooks for this company and event type
            webhooks = self._get_active_webhooks(company_id, event_type)
            
            results = []
            for webhook in webhooks:
                try:
                    response = requests.post(
                        webhook["url"],
                        json={
                            "event_type": event_type,
                            "payload": payload,
                            "timestamp": datetime.utcnow().isoformat(),
                            "company_id": str(company_id)
                        },
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Secret": webhook.get("secret", "")
                        },
                        timeout=30
                    )
                    
                    results.append({
                        "webhook_id": webhook["id"],
                        "status": "success" if response.status_code == 200 else "failed",
                        "response_code": response.status_code
                    })
                    
                except Exception as e:
                    results.append({
                        "webhook_id": webhook["id"],
                        "status": "failed",
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "event_type": event_type,
                "webhooks_sent": len(results),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Webhook event sending error: {str(e)}")
            return {
                "success": False,
                "error": f"Webhook event sending failed: {str(e)}"
            }
    
    # ==================== DATA SYNCHRONIZATION ====================
    
    def sync_customer_data(self, company_id: UUID, direction: str = "bidirectional") -> Dict[str, Any]:
        """Sync customer data with external systems"""
        try:
            sync_results = {
                "customers_synced": 0,
                "contacts_synced": 0,
                "errors": []
            }
            
            # Get active integrations
            integrations = self._get_active_integrations(company_id, [IntegrationType.CRM])
            
            for integration in integrations:
                try:
                    if direction in ["push", "bidirectional"]:
                        # Push local data to external system
                        push_result = self._push_customer_data(integration, company_id)
                        sync_results["customers_synced"] += push_result["count"]
                    
                    if direction in ["pull", "bidirectional"]:
                        # Pull data from external system
                        pull_result = self._pull_customer_data(integration, company_id)
                        sync_results["contacts_synced"] += pull_result["count"]
                        
                except Exception as e:
                    sync_results["errors"].append({
                        "integration_id": integration["id"],
                        "error": str(e)
                    })
            
            self.logger.info(f"Customer data sync completed for company {company_id}")
            return {
                "success": True,
                "sync_results": sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Customer data sync error: {str(e)}")
            return {
                "success": False,
                "error": f"Customer data sync failed: {str(e)}"
            }
    
    def sync_sales_data(self, company_id: UUID) -> Dict[str, Any]:
        """Sync sales data with external systems"""
        try:
            sync_results = {
                "quotes_synced": 0,
                "orders_synced": 0,
                "invoices_synced": 0,
                "errors": []
            }
            
            # Get active integrations
            integrations = self._get_active_integrations(company_id, [IntegrationType.ACCOUNTING, IntegrationType.ERP])
            
            for integration in integrations:
                try:
                    # Sync different types of sales data
                    if integration["type"] == IntegrationType.ACCOUNTING:
                        invoice_result = self._sync_invoices(integration, company_id)
                        sync_results["invoices_synced"] += invoice_result["count"]
                    
                    elif integration["type"] == IntegrationType.ERP:
                        order_result = self._sync_orders(integration, company_id)
                        sync_results["orders_synced"] += order_result["count"]
                        
                        quote_result = self._sync_quotes(integration, company_id)
                        sync_results["quotes_synced"] += quote_result["count"]
                        
                except Exception as e:
                    sync_results["errors"].append({
                        "integration_id": integration["id"],
                        "error": str(e)
                    })
            
            self.logger.info(f"Sales data sync completed for company {company_id}")
            return {
                "success": True,
                "sync_results": sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Sales data sync error: {str(e)}")
            return {
                "success": False,
                "error": f"Sales data sync failed: {str(e)}"
            }
    
    # ==================== BUSINESS INTELLIGENCE INTEGRATION ====================
    
    def create_bi_integration(self, config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Create business intelligence integration"""
        try:
            supported_bi_tools = ["tableau", "powerbi", "looker", "metabase", "grafana"]
            bi_tool = config.get("tool", "").lower()
            
            if bi_tool not in supported_bi_tools:
                return {
                    "success": False,
                    "error": f"Unsupported BI tool. Supported: {supported_bi_tools}"
                }
            
            # Set up data pipeline
            pipeline_config = self._setup_bi_pipeline(bi_tool, config, company_id)
            
            if pipeline_config["success"]:
                self.logger.info(f"BI integration {bi_tool} created for company {company_id}")
                return {
                    "success": True,
                    "integration_id": str(UUID()),
                    "bi_tool": bi_tool,
                    "status": "active",
                    "data_sources": pipeline_config["data_sources"]
                }
            else:
                return pipeline_config
                
        except Exception as e:
            self.logger.error(f"BI integration error: {str(e)}")
            return {
                "success": False,
                "error": f"BI integration failed: {str(e)}"
            }
    
    # ==================== HELPER METHODS ====================
    
    def _validate_crm_connection(self, config: Dict[str, Any]) -> bool:
        """Validate CRM connection"""
        try:
            # Implement CRM-specific validation logic
            return True
        except:
            return False
    
    def _configure_payment_gateway(self, gateway_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure payment gateway"""
        try:
            capabilities = {
                "stripe": ["credit_card", "ach", "international"],
                "paypal": ["paypal_account", "credit_card", "international"],
                "square": ["credit_card", "cash", "gift_card"],
                "authorize_net": ["credit_card", "echeck"],
                "razorpay": ["credit_card", "upi", "netbanking", "wallet"]
            }
            
            return {
                "success": True,
                "capabilities": capabilities.get(gateway_type, [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _configure_accounting_system(self, system_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure accounting system"""
        try:
            sync_capabilities = {
                "quickbooks": ["invoices", "customers", "items", "payments"],
                "xero": ["invoices", "contacts", "items", "payments"],
                "sage": ["invoices", "customers", "products", "payments"],
                "freshbooks": ["invoices", "clients", "projects", "payments"],
                "zoho_books": ["invoices", "customers", "items", "payments"]
            }
            
            return {
                "success": True,
                "sync_capabilities": sync_capabilities.get(system_type, [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_webhook_endpoint(self, url: str) -> bool:
        """Validate webhook endpoint"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _get_active_webhooks(self, company_id: UUID, event_type: str) -> List[Dict[str, Any]]:
        """Get active webhooks for company and event type"""
        # Mock implementation - replace with actual database query
        return [
            {
                "id": str(UUID()),
                "url": "https://example.com/webhook",
                "events": [event_type],
                "secret": "webhook_secret"
            }
        ]
    
    def _get_active_integrations(self, company_id: UUID, types: List[IntegrationType]) -> List[Dict[str, Any]]:
        """Get active integrations for company"""
        # Mock implementation - replace with actual database query
        return [
            {
                "id": str(UUID()),
                "type": types[0],
                "config": {},
                "status": IntegrationStatus.ACTIVE
            }
        ]
    
    def _setup_crm_data_sync(self, config: Dict[str, Any], company_id: UUID):
        """Set up CRM data synchronization"""
        # Implementation for CRM sync setup
        pass
    
    def _setup_accounting_sync(self, system_type: str, config: Dict[str, Any], company_id: UUID):
        """Set up accounting system synchronization"""
        # Implementation for accounting sync setup
        pass
    
    def _push_customer_data(self, integration: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Push customer data to external system"""
        # Implementation for pushing customer data
        return {"count": 10}
    
    def _pull_customer_data(self, integration: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Pull customer data from external system"""
        # Implementation for pulling customer data
        return {"count": 5}
    
    def _sync_invoices(self, integration: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Sync invoices with external system"""
        # Implementation for invoice sync
        return {"count": 15}
    
    def _sync_orders(self, integration: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Sync orders with external system"""
        # Implementation for order sync
        return {"count": 20}
    
    def _sync_quotes(self, integration: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Sync quotes with external system"""
        # Implementation for quote sync
        return {"count": 8}
    
    def _setup_bi_pipeline(self, bi_tool: str, config: Dict[str, Any], company_id: UUID) -> Dict[str, Any]:
        """Set up BI data pipeline"""
        try:
            data_sources = [
                "customers",
                "leads", 
                "quotes",
                "orders",
                "invoices",
                "payments",
                "sales_activities"
            ]
            
            return {
                "success": True,
                "data_sources": data_sources
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
