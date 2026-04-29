from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel
from .material import Quantity

LotStatus = Literal[
    "pending-iqc", "iqc-in-progress", "released",
    "quarantined", "rejected", "expired",
]


class AttachmentRef(BaseModel):
    id: str
    fileName: str
    mediaType: str
    size: Optional[int] = None
    uri: Optional[str] = None


class MaterialLot(BaseModel):
    id: str
    materialId: str
    supplierId: str
    supplierLotRef: Optional[str] = None
    quantity: Quantity
    receivedAt: str
    status: LotStatus
    expiresAt: Optional[str] = None
    storageLocation: Optional[str] = None
    coaId: Optional[str] = None
