"""
AirLynk — Pricing API Routes.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.pricing.repository.pricing_repository import PricingRepository
from backend.services.pricing.schemas.pricing import (
    FareEstimateRequest,
    FareEstimateResponse,
    PricingRuleCreate,
    PricingRuleResponse,
    PricingRuleUpdate,
)
from backend.services.pricing.service.pricing_service import PricingService
from backend.shared.database.session import get_db_session as get_db
from backend.shared.middleware.rbac import Role, get_current_user, require_roles

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/estimate", response_model=FareEstimateResponse)
async def estimate_fare(
    request: FareEstimateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Generate a fare estimate for a ride."""
    service = PricingService(db)
    try:
        return await service.calculate_fare(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/rules", response_model=list[PricingRuleResponse])
async def get_pricing_rules(
    city: str | None = None,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all pricing rules."""
    repo = PricingRepository(db)
    return await repo.get_all_rules(city=city)


@router.post("/rules", response_model=PricingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_pricing_rule(
    payload: PricingRuleCreate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new pricing rule."""
    service = PricingService(db)
    return await service.create_rule(payload)


@router.patch("/rules/{rule_id}", response_model=PricingRuleResponse)
async def update_pricing_rule(
    rule_id: uuid.UUID,
    payload: PricingRuleUpdate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update an existing pricing rule."""
    service = PricingService(db)
    try:
        return await service.update_rule(rule_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
