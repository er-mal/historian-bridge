from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Cell(BaseModel):
    id: str
    serial: Optional[str] = None
    lotId: str
    chemistry: str
    formatCode: str
    capacityNominal_Ah: float
    capacityMeasured_Ah: Optional[float] = None
    ocv_V: Optional[float] = None
    internalResistance_mOhm: Optional[float] = None
    productionOrderId: Optional[str] = None


class Module(BaseModel):
    id: str
    serial: str
    cellIds: list[str] = Field(default_factory=list)
    topology: str
    productionOrderId: Optional[str] = None


class Pack(BaseModel):
    id: str
    serial: str
    moduleIds: list[str] = Field(default_factory=list)
    customer: Optional[str] = None
    application: Literal["EV", "ESS", "industrial", "marine", "aerospace", "other"]
    bmsHardwareRev: Optional[str] = None
    bmsFirmwareRev: Optional[str] = None
    productionOrderId: Optional[str] = None
