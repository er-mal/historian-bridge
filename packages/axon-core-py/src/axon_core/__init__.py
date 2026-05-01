"""axon_core — Pydantic domain models, mirror of @axon/core (TypeScript).

Keep field names identical to the TS package so JSON round-trips cleanly.
"""
from .material import Material, MaterialCategory, MaterialSpec, Quantity, SpecRange, Supplier
from .lot import AttachmentRef, LotStatus, MaterialLot
from .coa import CoA, CoAMeasurement, MeasurementResult, evaluate, roll_up
from .production import KanbanCard, OperationStep, ProdStatus, ProductionOrder
from .quality import NonConformity, QualityOrder, QualityState, QuarantineOrder, Severity
from .station import (
    CarrierType,
    StationIO,
    StationSpec,
    TestKind,
    TestResult,
    TestSpec,
    TestStep,
)
from .historian import HistorianPoint, HistorianTag, Quality, TagQuery

__all__ = [
    "AttachmentRef", "CarrierType", "CoA", "CoAMeasurement",
    "HistorianPoint", "HistorianTag", "KanbanCard",
    "LotStatus", "Material", "MaterialCategory", "MaterialLot", "MaterialSpec",
    "MeasurementResult", "NonConformity", "OperationStep",
    "ProdStatus", "ProductionOrder", "Quality", "QualityOrder",
    "QualityState", "Quantity", "QuarantineOrder", "Severity", "SpecRange",
    "StationIO", "StationSpec", "Supplier", "TagQuery", "TestKind",
    "TestResult", "TestSpec", "TestStep", "evaluate", "roll_up",
]

__version__ = "0.1.0"
