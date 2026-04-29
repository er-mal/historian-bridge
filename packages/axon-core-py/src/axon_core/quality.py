from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel

Severity = Literal[1, 2, 3, 4]
QualityState = Literal["open", "investigation", "containment", "resolved", "closed"]


class NonConformity(BaseModel):
    id: str
    productionOrderId: Optional[str] = None
    lotId: Optional[str] = None
    itemRef: Optional[str] = None
    reportedAt: str
    reportedBy: str
    severity: Severity
    state: QualityState
    description: str
    rootCause: Optional[str] = None
    capa: Optional[str] = None
    closedAt: Optional[str] = None


class QuarantineOrder(BaseModel):
    id: str
    lotId: str
    reason: str
    createdAt: str
    releasedAt: Optional[str] = None
    rejectedAt: Optional[str] = None
    releasedBy: Optional[str] = None


class QualityOrder(BaseModel):
    id: str
    productionOrderId: Optional[str] = None
    lotId: Optional[str] = None
    type: Literal["incoming", "in-process", "outgoing"]
    testPlanId: Optional[str] = None
    state: QualityState
