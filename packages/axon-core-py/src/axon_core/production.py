from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

ProdStatus = Literal[
    "created", "estimated", "scheduled", "released", "started",
    "reportedFinished", "ended", "cancelled",
]


class OperationStep(BaseModel):
    oprNum: int
    oprId: str
    oprPriority: int
    jobIdentification: Optional[str] = None
    capacityCheck: Optional[bool] = None
    resourceId: Optional[str] = None
    oprDateTime: Optional[str] = None
    setupTimeSec: Optional[float] = None
    runTimePerPieceSec: Optional[float] = None


class ProductionOrder(BaseModel):
    id: str
    prodId: str
    itemId: str
    qtyPlanned: float
    qtyReported: float = 0.0
    status: ProdStatus
    operations: list[OperationStep] = Field(default_factory=list)
    batchNumber: Optional[str] = None
    inventBatchId: Optional[str] = None
    createdAt: Optional[str] = None
    scheduledStart: Optional[str] = None
    scheduledEnd: Optional[str] = None


class KanbanCard(BaseModel):
    id: str
    itemId: str
    qty: float
    status: Literal["empty", "in-transit", "filled", "consumed"]
    fromLocation: str
    toLocation: str
    productionOrderId: Optional[str] = None
