"""
Enhanced Sales Dashboard Routes
Provides comprehensive sales dashboard with real-time analytics
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID

from bheem_core.core.database import get_db
from bheem_core.modules.auth.core.services.permissions_service import (
    require_roles, require_api_permission, get_current_user_id, get_current_company_id
)
from bheem_core.shared.models import UserRole

router = APIRouter(prefix="/dashboard", tags=["Sales Dashboard"])

# ==================== EXECUTIVE DASHBOARD ====================

@router.get("/executive/overview",
            dependencies=[
                Depends(lambda: require_api_permission("sales.dashboard.executive")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def get_executive_dashboard(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, quarterly"),
    compare_previous: bool = Query(True, description="Compare with previous period"),
    db = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get executive sales dashboard overview"""
    
    dashboard_data = {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "kpi_summary": {
            "total_revenue": {
                "current": 425000.00,
                "previous": 380000.00,
                "change_percent": 11.8,
                "trend": "up"
            },
            "deals_closed": {
                "current": 42,
                "previous": 38,
                "change_percent": 10.5,
                "trend": "up"
            },
            "average_deal_size": {
                "current": 10119.05,
                "previous": 10000.00,
                "change_percent": 1.2,
                "trend": "up"
            },
            "win_rate": {
                "current": 0.68,
                "previous": 0.65,
                "change_percent": 4.6,
                "trend": "up"
            },
            "sales_cycle_days": {
                "current": 42,
                "previous": 45,
                "change_percent": -6.7,
                "trend": "down"
            }
        },
        "revenue_trend": [
            {"period": "Week 1", "revenue": 98000.00, "target": 95000.00},
            {"period": "Week 2", "revenue": 105000.00, "target": 95000.00},
            {"period": "Week 3", "revenue": 112000.00, "target": 95000.00},
            {"period": "Week 4", "revenue": 110000.00, "target": 95000.00}
        ],
        "pipeline_health": {
            "total_value": 1250000.00,
            "weighted_value": 875000.00,
            "deals_by_stage": {
                "prospecting": {"count": 25, "value": 375000.00},
                "qualification": {"count": 18, "value": 270000.00},
                "proposal": {"count": 15, "value": 300000.00},
                "negotiation": {"count": 12, "value": 180000.00},
                "closing": {"count": 8, "value": 125000.00}
            },
            "health_score": 0.85
        },
        "team_performance": {
            "top_performers": [
                {"name": "Sarah Johnson", "revenue": 125000.00, "deals": 12},
                {"name": "John Smith", "revenue": 120000.00, "deals": 11},
                {"name": "Mike Wilson", "revenue": 95000.00, "deals": 9}
            ],
            "quota_attainment": 0.78,
            "activity_trends": {
                "calls_made": 450,
                "emails_sent": 1200,
                "meetings_held": 185
            }
        },
        "alerts": [
            {
                "type": "warning",
                "message": "Pipeline value down 5% from last month",
                "priority": "medium"
            },
            {
                "type": "success",
                "message": "Q1 revenue target exceeded by 12%",
                "priority": "high"
            }
        ]
    }
    
    return dashboard_data

# ==================== SALES MANAGER DASHBOARD ====================

@router.get("/manager/team-performance",
            dependencies=[
                Depends(lambda: require_api_permission("sales.dashboard.manager")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER]))
            ])
async def get_manager_dashboard(
    team_id: Optional[UUID] = Query(None, description="Specific team ID"),
    include_individual: bool = Query(True, description="Include individual rep data"),
    db = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales manager dashboard with team performance"""
    
    manager_dashboard = {
        "team_overview": {
            "team_size": 8,
            "active_deals": 45,
            "monthly_revenue": 425000.00,
            "quota_attainment": 0.78,
            "team_health_score": 0.82
        },
        "individual_performance": [
            {
                "rep_id": str(UUID()),
                "rep_name": "Sarah Johnson",
                "territory": "North America",
                "metrics": {
                    "revenue": 125000.00,
                    "quota": 150000.00,
                    "quota_attainment": 0.833,
                    "deals_closed": 12,
                    "pipeline_value": 180000.00,
                    "activities_completed": 145
                },
                "performance_trend": "improving",
                "coaching_priority": "low"
            },
            {
                "rep_id": str(UUID()),
                "rep_name": "John Smith",
                "territory": "North America",
                "metrics": {
                    "revenue": 120000.00,
                    "quota": 150000.00,
                    "quota_attainment": 0.800,
                    "deals_closed": 11,
                    "pipeline_value": 165000.00,
                    "activities_completed": 138
                },
                "performance_trend": "stable",
                "coaching_priority": "medium"
            },
            {
                "rep_id": str(UUID()),
                "rep_name": "Mike Wilson",
                "territory": "Europe",
                "metrics": {
                    "revenue": 95000.00,
                    "quota": 140000.00,
                    "quota_attainment": 0.679,
                    "deals_closed": 9,
                    "pipeline_value": 120000.00,
                    "activities_completed": 102
                },
                "performance_trend": "declining",
                "coaching_priority": "high"
            }
        ] if include_individual else [],
        "team_activities": {
            "daily_calls": 85,
            "weekly_demos": 22,
            "monthly_proposals": 18,
            "follow_ups_pending": 34
        },
        "pipeline_analysis": {
            "stage_distribution": {
                "prospecting": 28,
                "qualification": 22,
                "proposal": 18,
                "negotiation": 15,
                "closing": 12
            },
            "deal_velocity": {
                "average_days": 42,
                "fastest_deals": 28,
                "slowest_deals": 65
            },
            "win_loss_analysis": {
                "won": 38,
                "lost": 18,
                "win_rate": 0.678,
                "loss_reasons": {
                    "price": 8,
                    "competitor": 6,
                    "timing": 4
                }
            }
        },
        "coaching_insights": [
            {
                "rep_name": "Mike Wilson",
                "insight": "Needs help with closing techniques",
                "priority": "high",
                "action": "Schedule closing skills training"
            },
            {
                "rep_name": "John Smith",
                "insight": "Strong performer, could mentor others",
                "priority": "medium",
                "action": "Assign mentoring responsibilities"
            }
        ]
    }
    
    return manager_dashboard

# ==================== SALES REP DASHBOARD ====================

@router.get("/rep/personal-dashboard",
            dependencies=[
                Depends(lambda: require_api_permission("sales.dashboard.rep")),
                Depends(require_roles([UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_REP]))
            ])
async def get_rep_dashboard(
    rep_id: Optional[UUID] = Query(None, description="Rep ID (defaults to current user)"),
    include_tasks: bool = Query(True, description="Include task list"),
    db = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
    company_id: UUID = Depends(get_current_company_id)
):
    """Get sales rep personal dashboard"""
    
    rep_dashboard = {
        "personal_metrics": {
            "revenue_ytd": 125000.00,
            "quota_ytd": 150000.00,
            "quota_attainment": 0.833,
            "deals_closed": 12,
            "pipeline_value": 180000.00,
            "activities_this_week": 28,
            "calls_made": 45,
            "emails_sent": 120
        },
        "goals_progress": {
            "monthly_revenue": {
                "target": 12500.00,
                "current": 10400.00,
                "progress": 0.832
            },
            "monthly_deals": {
                "target": 3,
                "current": 2,
                "progress": 0.667
            },
            "activity_goals": {
                "calls_per_day": {"target": 8, "current": 6},
                "emails_per_day": {"target": 15, "current": 12},
                "meetings_per_week": {"target": 5, "current": 4}
            }
        },
        "pipeline_overview": {
            "deals_by_stage": [
                {
                    "stage": "Prospecting",
                    "count": 8,
                    "value": 45000.00,
                    "deals": [
                        {"company": "TechCorp", "value": 15000.00, "days_in_stage": 5},
                        {"company": "StartUp Inc", "value": 8000.00, "days_in_stage": 12}
                    ]
                },
                {
                    "stage": "Qualification",
                    "count": 6,
                    "value": 55000.00,
                    "deals": [
                        {"company": "BigCorp", "value": 25000.00, "days_in_stage": 8},
                        {"company": "MediumCo", "value": 18000.00, "days_in_stage": 15}
                    ]
                },
                {
                    "stage": "Proposal",
                    "count": 4,
                    "value": 65000.00,
                    "deals": [
                        {"company": "Enterprise Ltd", "value": 35000.00, "days_in_stage": 10},
                        {"company": "Growth Co", "value": 20000.00, "days_in_stage": 6}
                    ]
                },
                {
                    "stage": "Closing",
                    "count": 2,
                    "value": 15000.00,
                    "deals": [
                        {"company": "ReadyBuyer", "value": 8000.00, "days_in_stage": 3},
                        {"company": "AlmostThere", "value": 7000.00, "days_in_stage": 5}
                    ]
                }
            ],
            "next_actions": [
                {"deal": "TechCorp", "action": "Schedule demo", "due_date": "2024-01-15"},
                {"deal": "BigCorp", "action": "Send proposal", "due_date": "2024-01-12"},
                {"deal": "Enterprise Ltd", "action": "Follow up on proposal", "due_date": "2024-01-10"}
            ]
        },
        "recent_activities": [
            {
                "type": "call",
                "company": "TechCorp",
                "duration": "30 min",
                "outcome": "Scheduled demo",
                "timestamp": "2024-01-08T14:30:00Z"
            },
            {
                "type": "email",
                "company": "BigCorp",
                "subject": "Proposal follow-up",
                "status": "opened",
                "timestamp": "2024-01-08T10:15:00Z"
            },
            {
                "type": "meeting",
                "company": "Enterprise Ltd",
                "duration": "45 min",
                "outcome": "Negotiation started",
                "timestamp": "2024-01-07T16:00:00Z"
            }
        ],
        "tasks": [
            {
                "task_id": str(UUID()),
                "title": "Follow up with TechCorp demo",
                "due_date": "2024-01-15",
                "priority": "high",
                "type": "follow_up"
            },
            {
                "task_id": str(UUID()),
                "title": "Prepare proposal for BigCorp",
                "due_date": "2024-01-12",
                "priority": "medium",
                "type": "proposal"
            },
            {
                "task_id": str(UUID()),
                "title": "Update CRM with meeting notes",
                "due_date": "2024-01-10",
                "priority": "low",
                "type": "admin"
            }
        ] if include_tasks else [],
        "performance_insights": [
            "Your closing rate is 15% above team average",
            "Consider increasing daily call volume by 2 calls",
            "Best performing day: Tuesday (highest response rate)"
        ]
    }
    
    return rep_dashboard

# ==================== REAL-TIME DASHBOARD ====================

@router.get("/realtime/activity-feed")
async def get_realtime_activity_feed(
    limit: int = Query(50, description="Number of activities to return"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    company_id: UUID = None
):
    """Get real-time sales activity feed"""
    
    activities = [
        {
            "activity_id": str(UUID()),
            "type": "deal_won",
            "message": "Sarah Johnson closed deal with TechCorp for $25,000",
            "timestamp": datetime.utcnow().isoformat(),
            "user": "Sarah Johnson",
            "value": 25000.00,
            "icon": "🎉"
        },
        {
            "activity_id": str(UUID()),
            "type": "demo_scheduled",
            "message": "John Smith scheduled demo with BigCorp",
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "user": "John Smith",
            "value": None,
            "icon": "📅"
        },
        {
            "activity_id": str(UUID()),
            "type": "proposal_sent",
            "message": "Mike Wilson sent proposal to StartUp Inc",
            "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            "user": "Mike Wilson",
            "value": None,
            "icon": "📝"
        },
        {
            "activity_id": str(UUID()),
            "type": "lead_qualified",
            "message": "New qualified lead: Enterprise Solutions Ltd",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "user": "System",
            "value": None,
            "icon": "✅"
        },
        {
            "activity_id": str(UUID()),
            "type": "meeting_completed",
            "message": "Sarah Johnson completed discovery call with Growth Co",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "user": "Sarah Johnson",
            "value": None,
            "icon": "📞"
        }
    ]
    
    # Filter by activity type if specified
    if activity_type:
        activities = [a for a in activities if a["type"] == activity_type]
    
    return {
        "activities": activities[:limit],
        "total": len(activities),
        "last_updated": datetime.utcnow().isoformat()
    }

# ==================== DASHBOARD WIDGETS ====================

@router.get("/widgets/revenue-chart")
async def get_revenue_chart_widget(
    period: str = Query("monthly", description="Chart period"),
    chart_type: str = Query("line", description="Chart type: line, bar, area"),
    company_id: UUID = None
):
    """Get revenue chart widget data"""
    
    chart_data = {
        "chart_type": chart_type,
        "period": period,
        "data": [
            {"period": "Jan", "revenue": 98000, "target": 95000, "previous_year": 85000},
            {"period": "Feb", "revenue": 105000, "target": 95000, "previous_year": 92000},
            {"period": "Mar", "revenue": 112000, "target": 95000, "previous_year": 98000},
            {"period": "Apr", "revenue": 108000, "target": 95000, "previous_year": 105000},
            {"period": "May", "revenue": 115000, "target": 95000, "previous_year": 108000},
            {"period": "Jun", "revenue": 122000, "target": 95000, "previous_year": 115000}
        ],
        "summary": {
            "total_revenue": 660000,
            "growth_rate": 0.125,
            "target_achievement": 1.16
        }
    }
    
    return chart_data

@router.get("/widgets/pipeline-funnel")
async def get_pipeline_funnel_widget(
    include_conversion_rates: bool = Query(True, description="Include conversion rates"),
    company_id: UUID = None
):
    """Get pipeline funnel widget data"""
    
    funnel_data = {
        "stages": [
            {
                "stage": "Leads",
                "count": 150,
                "value": 750000,
                "conversion_rate": 0.67 if include_conversion_rates else None
            },
            {
                "stage": "Qualified",
                "count": 100,
                "value": 600000,
                "conversion_rate": 0.75 if include_conversion_rates else None
            },
            {
                "stage": "Proposal",
                "count": 75,
                "value": 525000,
                "conversion_rate": 0.80 if include_conversion_rates else None
            },
            {
                "stage": "Negotiation",
                "count": 60,
                "value": 450000,
                "conversion_rate": 0.70 if include_conversion_rates else None
            },
            {
                "stage": "Closed Won",
                "count": 42,
                "value": 315000,
                "conversion_rate": None
            }
        ],
        "overall_conversion": 0.28,
        "average_deal_size": 7500
    }
    
    return funnel_data

@router.get("/widgets/team-performance")
async def get_team_performance_widget(
    metric: str = Query("revenue", description="Performance metric"),
    top_n: int = Query(5, description="Number of top performers to show"),
    company_id: UUID = None
):
    """Get team performance widget data"""
    
    performance_data = {
        "metric": metric,
        "performers": [
            {
                "name": "Sarah Johnson",
                "value": 125000 if metric == "revenue" else 12,
                "quota": 150000 if metric == "revenue" else 15,
                "achievement": 0.833,
                "trend": "up"
            },
            {
                "name": "John Smith",
                "value": 120000 if metric == "revenue" else 11,
                "quota": 150000 if metric == "revenue" else 15,
                "achievement": 0.800,
                "trend": "stable"
            },
            {
                "name": "Mike Wilson",
                "value": 95000 if metric == "revenue" else 9,
                "quota": 140000 if metric == "revenue" else 12,
                "achievement": 0.679,
                "trend": "down"
            }
        ][:top_n],
        "team_average": 113333 if metric == "revenue" else 10.7,
        "top_performer": "Sarah Johnson"
    }
    
    return performance_data

