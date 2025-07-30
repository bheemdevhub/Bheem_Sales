"""
Advanced Business Features Routes for Sales Module
Provides enterprise-grade business features and automation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole

router = APIRouter(prefix="/business-features", tags=["Advanced Business Features"])

# ==================== SALES FORECASTING ====================

@router.get("/forecasting/revenue",
            dependencies=[
                Depends(lambda: require_api_permission("sales.forecasting.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def get_revenue_forecast(
    period: str = Query("quarterly", description="Forecast period: monthly, quarterly, yearly"),
    confidence_level: float = Query(0.85, ge=0.7, le=0.95, description="Forecast confidence level"),
    include_pipeline: bool = Query(True, description="Include pipeline data"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get revenue forecasting with AI-powered predictions"""
    
    # Mock forecast data - replace with actual ML model
    forecast_data = {
        "period": period,
        "confidence_level": confidence_level,
        "forecast": {
            "current_month": {
                "predicted_revenue": 145000.50,
                "confidence_range": {
                    "low": 135000.00,
                    "high": 155000.00
                },
                "key_factors": [
                    "Historical sales trends",
                    "Pipeline velocity",
                    "Seasonal patterns",
                    "Market conditions"
                ]
            },
            "next_month": {
                "predicted_revenue": 152000.75,
                "confidence_range": {
                    "low": 140000.00,
                    "high": 165000.00
                }
            }
        },
        "pipeline_analysis": {
            "total_pipeline_value": 450000.00,
            "weighted_pipeline": 315000.00,
            "conversion_probability": 0.72,
            "average_deal_size": 15000.00,
            "sales_cycle_days": 45
        },
        "recommendations": [
            "Focus on high-value prospects in pipeline",
            "Accelerate deals in final stages",
            "Increase marketing efforts in Q2",
            "Review pricing strategy for better margins"
        ]
    }
    
    return forecast_data

@router.get("/forecasting/pipeline",
            dependencies=[
                Depends(lambda: require_api_permission("sales.forecasting.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def get_pipeline_forecast(
    rep_id: Optional[UUID] = Query(None, description="Filter by sales rep"),
    territory: Optional[str] = Query(None, description="Filter by territory"),
    product_category: Optional[str] = Query(None, description="Filter by product category"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales pipeline forecasting"""
    
    pipeline_forecast = {
        "total_opportunities": 45,
        "total_value": 675000.00,
        "weighted_value": 472500.00,
        "stages": [
            {
                "stage": "Qualification",
                "count": 15,
                "value": 225000.00,
                "probability": 0.25,
                "weighted_value": 56250.00
            },
            {
                "stage": "Proposal",
                "count": 12,
                "value": 180000.00,
                "probability": 0.50,
                "weighted_value": 90000.00
            },
            {
                "stage": "Negotiation",
                "count": 8,
                "value": 120000.00,
                "probability": 0.75,
                "weighted_value": 90000.00
            },
            {
                "stage": "Closing",
                "count": 10,
                "value": 150000.00,
                "probability": 0.90,
                "weighted_value": 135000.00
            }
        ],
        "conversion_metrics": {
            "average_deal_size": 15000.00,
            "win_rate": 0.68,
            "sales_cycle_days": 42,
            "velocity": 3571.43  # weighted_value / sales_cycle_days
        }
    }
    
    return pipeline_forecast

# ==================== SALES TERRITORY MANAGEMENT ====================

@router.get("/territory/performance",
            dependencies=[
                Depends(lambda: require_api_permission("sales.territory.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def get_territory_performance(
    period: str = Query("ytd", description="Performance period: mtd, qtd, ytd"),
    include_reps: bool = Query(True, description="Include rep performance"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get territory performance analytics"""
    
    territory_data = {
        "territories": [
            {
                "territory_id": "north_america",
                "territory_name": "North America",
                "performance": {
                    "revenue": 245000.00,
                    "quota": 300000.00,
                    "quota_attainment": 0.817,
                    "deals_closed": 18,
                    "opportunities": 25
                },
                "reps": [
                    {
                        "rep_id": str(UUID()),
                        "rep_name": "John Smith",
                        "revenue": 125000.00,
                        "quota": 150000.00,
                        "quota_attainment": 0.833
                    },
                    {
                        "rep_id": str(UUID()),
                        "rep_name": "Sarah Johnson",
                        "revenue": 120000.00,
                        "quota": 150000.00,
                        "quota_attainment": 0.800
                    }
                ] if include_reps else []
            },
            {
                "territory_id": "europe",
                "territory_name": "Europe",
                "performance": {
                    "revenue": 180000.00,
                    "quota": 250000.00,
                    "quota_attainment": 0.720,
                    "deals_closed": 15,
                    "opportunities": 22
                },
                "reps": [] if not include_reps else [
                    {
                        "rep_id": str(UUID()),
                        "rep_name": "Hans Mueller",
                        "revenue": 95000.00,
                        "quota": 125000.00,
                        "quota_attainment": 0.760
                    }
                ]
            }
        ],
        "summary": {
            "total_revenue": 425000.00,
            "total_quota": 550000.00,
            "overall_attainment": 0.773,
            "top_performing_territory": "North America",
            "improvement_opportunities": ["Europe territory needs focus"]
        }
    }
    
    return territory_data

# ==================== SALES INTELLIGENCE ====================

@router.get("/intelligence/insights",
            dependencies=[
                Depends(lambda: require_api_permission("sales.intelligence.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def get_sales_insights(
    insight_type: str = Query("all", description="Type: conversion, behavior, performance, competitive"),
    customer_id: Optional[UUID] = Query(None, description="Customer-specific insights"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get AI-powered sales insights"""
    
    insights = {
        "conversion_insights": [
            {
                "insight": "Deals with demos have 85% higher conversion rate",
                "confidence": 0.92,
                "action": "Schedule more product demonstrations",
                "impact": "high"
            },
            {
                "insight": "Proposals sent on Tuesday have 23% better response rate",
                "confidence": 0.78,
                "action": "Optimize proposal timing",
                "impact": "medium"
            }
        ],
        "behavioral_insights": [
            {
                "insight": "Customers who engage with pricing page 3+ times are 60% more likely to buy",
                "confidence": 0.85,
                "action": "Prioritize multi-visit prospects",
                "impact": "high"
            },
            {
                "insight": "Email engagement drops after 3 follow-ups",
                "confidence": 0.81,
                "action": "Switch to phone calls after 3 emails",
                "impact": "medium"
            }
        ],
        "performance_insights": [
            {
                "insight": "Top reps spend 40% more time on discovery calls",
                "confidence": 0.88,
                "action": "Extend discovery call duration",
                "impact": "high"
            },
            {
                "insight": "CRM data quality correlates with 25% higher close rates",
                "confidence": 0.83,
                "action": "Improve data entry practices",
                "impact": "medium"
            }
        ],
        "competitive_insights": [
            {
                "insight": "We lose 65% of deals to Competitor A on price",
                "confidence": 0.79,
                "action": "Review pricing strategy and value proposition",
                "impact": "high"
            },
            {
                "insight": "Feature X is mentioned in 80% of won deals",
                "confidence": 0.86,
                "action": "Lead with Feature X in demos",
                "impact": "high"
            }
        ]
    }
    
    # Filter by insight type if specified
    if insight_type != "all":
        insights = {f"{insight_type}_insights": insights.get(f"{insight_type}_insights", [])}
    
    return insights

# ==================== SALES COLLABORATION ====================

@router.post("/collaboration/deal-room",
             dependencies=[
                 Depends(lambda: require_api_permission("sales.collaboration.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
             ])
async def create_deal_room(
    deal_room_data: Dict[str, Any] = Body(...),
    db = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Create collaborative deal room"""
    
    deal_room = {
        "deal_room_id": str(UUID()),
        "deal_name": deal_room_data["deal_name"],
        "customer_name": deal_room_data["customer_name"],
        "deal_value": deal_room_data["deal_value"],
        "created_by": str(current_user_id),
        "created_at": datetime.utcnow().isoformat(),
        "team_members": deal_room_data.get("team_members", []),
        "documents": [],
        "communications": [],
        "timeline": [
            {
                "event": "Deal room created",
                "timestamp": datetime.utcnow().isoformat(),
                "user": str(current_user_id)
            }
        ],
        "status": "active"
    }
    
    return {
        "success": True,
        "deal_room": deal_room,
        "message": "Deal room created successfully"
    }

@router.get("/collaboration/deal-rooms",
            dependencies=[
                Depends(lambda: require_api_permission("sales.collaboration.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def list_deal_rooms(
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """List collaborative deal rooms"""
    
    deal_rooms = [
        {
            "deal_room_id": str(UUID()),
            "deal_name": "Enterprise Software License",
            "customer_name": "Acme Corp",
            "deal_value": 50000.00,
            "status": "active",
            "team_members": 4,
            "last_activity": datetime.utcnow().isoformat(),
            "stage": "negotiation"
        },
        {
            "deal_room_id": str(UUID()),
            "deal_name": "Cloud Migration Services",
            "customer_name": "TechStart Inc",
            "deal_value": 75000.00,
            "status": "active",
            "team_members": 6,
            "last_activity": datetime.utcnow().isoformat(),
            "stage": "proposal"
        }
    ]
    
    # Apply filters
    if status:
        deal_rooms = [room for room in deal_rooms if room["status"] == status]
    
    return {
        "deal_rooms": deal_rooms,
        "total": len(deal_rooms)
    }

# ==================== SALES GAMIFICATION ====================

@router.get("/gamification/leaderboard",
            dependencies=[
                Depends(lambda: require_api_permission("sales.gamification.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def get_sales_leaderboard(
    period: str = Query("monthly", description="Leaderboard period: weekly, monthly, quarterly"),
    metric: str = Query("revenue", description="Metric: revenue, deals, activities, calls"),
    team_only: bool = Query(False, description="Show only team members"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales gamification leaderboard"""
    
    leaderboard = {
        "period": period,
        "metric": metric,
        "rankings": [
            {
                "rank": 1,
                "rep_id": str(UUID()),
                "rep_name": "Sarah Johnson",
                "value": 125000.00 if metric == "revenue" else 18,
                "badge": "🥇 Top Performer",
                "streak": 3,
                "achievement": "Revenue Leader"
            },
            {
                "rank": 2,
                "rep_id": str(UUID()),
                "rep_name": "John Smith",
                "value": 120000.00 if metric == "revenue" else 16,
                "badge": "🥈 Strong Performer",
                "streak": 2,
                "achievement": "Deal Closer"
            },
            {
                "rank": 3,
                "rep_id": str(UUID()),
                "rep_name": "Mike Wilson",
                "value": 95000.00 if metric == "revenue" else 12,
                "badge": "🥉 Rising Star",
                "streak": 1,
                "achievement": "Activity Champion"
            }
        ],
        "achievements": [
            {
                "title": "Deal Closer",
                "description": "Close 5 deals in a month",
                "badge": "🎯",
                "unlocked_by": ["John Smith", "Sarah Johnson"]
            },
            {
                "title": "Revenue Leader",
                "description": "Achieve highest revenue in period",
                "badge": "💰",
                "unlocked_by": ["Sarah Johnson"]
            }
        ],
        "team_stats": {
            "total_participants": 12,
            "average_performance": 87500.00 if metric == "revenue" else 13,
            "improvement_rate": 0.15
        }
    }
    
    return leaderboard

# ==================== SALES COACHING ====================

@router.get("/coaching/recommendations",
            dependencies=[
                Depends(lambda: require_api_permission("sales.coaching.read")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def get_coaching_recommendations(
    rep_id: Optional[UUID] = Query(None, description="Specific rep ID"),
    focus_area: Optional[str] = Query(None, description="Focus area: prospecting, closing, presentation"),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get AI-powered coaching recommendations"""
    
    recommendations = {
        "rep_analysis": {
            "rep_id": str(rep_id) if rep_id else "all",
            "strengths": [
                "Excellent at discovery calls",
                "Strong product knowledge",
                "Good customer relationship building"
            ],
            "improvement_areas": [
                "Closing techniques need improvement",
                "Follow-up consistency",
                "Pipeline management"
            ],
            "performance_trend": "improving"
        },
        "coaching_actions": [
            {
                "priority": "high",
                "area": "Closing",
                "recommendation": "Practice assumptive close techniques",
                "resources": [
                    "Closing techniques training video",
                    "Role-play scenarios",
                    "Peer mentoring with top closer"
                ],
                "timeline": "2 weeks"
            },
            {
                "priority": "medium",
                "area": "Follow-up",
                "recommendation": "Implement systematic follow-up process",
                "resources": [
                    "Follow-up templates",
                    "CRM automation setup",
                    "Time management training"
                ],
                "timeline": "1 week"
            }
        ],
        "skill_development": [
            {
                "skill": "Objection Handling",
                "current_level": "intermediate",
                "target_level": "advanced",
                "training_modules": [
                    "Common objections workshop",
                    "Competitive positioning",
                    "Value-based selling"
                ]
            }
        ]
    }
    
    return recommendations

# ==================== SALES PERFORMANCE OPTIMIZATION ====================

@router.post("/optimization/process-analysis",
             dependencies=[
                 Depends(lambda: require_api_permission("sales.optimization.create")),
                 Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
             ])
async def analyze_sales_process(
    analysis_config: Dict[str, Any] = Body(...),
    db = Depends(get_db),
    company_id: UUID = Depends(get_current_company_id)
):
    """Analyze sales process for optimization opportunities"""
    
    analysis = {
        "process_stages": [
            {
                "stage": "Lead Generation",
                "efficiency_score": 0.78,
                "bottlenecks": ["Low conversion from marketing"],
                "recommendations": ["Improve lead qualification criteria"]
            },
            {
                "stage": "Qualification",
                "efficiency_score": 0.85,
                "bottlenecks": ["Long qualification time"],
                "recommendations": ["Implement BANT framework"]
            },
            {
                "stage": "Proposal",
                "efficiency_score": 0.72,
                "bottlenecks": ["Delayed proposal approvals"],
                "recommendations": ["Streamline approval process"]
            },
            {
                "stage": "Closing",
                "efficiency_score": 0.68,
                "bottlenecks": ["Extended decision cycles"],
                "recommendations": ["Create urgency factors"]
            }
        ],
        "overall_efficiency": 0.76,
        "optimization_opportunities": [
            {
                "opportunity": "Automate follow-up sequences",
                "impact": "high",
                "effort": "medium",
                "roi_estimate": 1.25
            },
            {
                "opportunity": "Implement lead scoring",
                "impact": "high",
                "effort": "low",
                "roi_estimate": 1.45
            }
        ]
    }
    
    return analysis

