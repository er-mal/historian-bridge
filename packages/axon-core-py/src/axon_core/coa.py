from __future__ import annotations
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field
from .lot import AttachmentRef

MeasurementResult = Literal["pass", "fail", "review", "informational"]


class _Spec(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    lt: Optional[float] = None
    gt: Optional[float] = None


class CoAMeasurement(BaseModel):
    parameter: str
    value: Union[float, str]
    unit: str
    spec: Optional[_Spec] = None
    result: MeasurementResult
    notes: Optional[str] = None


class CoA(BaseModel):
    id: str
    lotId: str
    supplierId: str
    issuedAt: str
    validatedBy: Optional[str] = None
    measurements: list[CoAMeasurement] = Field(default_factory=list)
    attachments: Optional[list[AttachmentRef]] = None
    overall: MeasurementResult


def roll_up(measurements: list[CoAMeasurement]) -> MeasurementResult:
    if any(m.result == "fail" for m in measurements):
        return "fail"
    if any(m.result == "review" for m in measurements):
        return "review"
    return "pass"


def evaluate(value: float, spec: _Spec) -> MeasurementResult:
    if spec.min is not None and value < spec.min:
        return "fail"
    if spec.max is not None and value > spec.max:
        return "fail"
    if spec.lt is not None and not (value < spec.lt):
        return "fail"
    if spec.gt is not None and not (value > spec.gt):
        return "fail"
    return "pass"
