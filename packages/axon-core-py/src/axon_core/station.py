from __future__ import annotations
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field

CarrierType = Literal["tray", "pallet", "conveyor", "agv", "manual"]

TestKind = Literal[
    "visual", "dimensional", "leak-helium", "leak-pressure-decay",
    "isolation", "hipot", "hvil", "insulation-resistance",
    "weld-pull", "weld-resistance", "torque", "ocv", "dcir",
    "capacity", "thermal-imaging", "communication", "firmware-flash", "other",
]


class StationIO(BaseModel):
    itemRef: str
    carrier: CarrierType
    fixtureId: Optional[str] = None


class TestSpec(BaseModel):
    parameter: str
    unit: str
    min: Optional[float] = None
    max: Optional[float] = None
    rampMs: Optional[float] = None
    holdMs: Optional[float] = None
    samples: Optional[int] = None


class TestStep(BaseModel):
    id: str
    kind: TestKind
    spec: TestSpec
    required: bool = True
    runOnPriorFail: bool = False


class StationSpec(BaseModel):
    id: str
    name: str
    line: str
    position: int
    inputs: list[StationIO] = Field(default_factory=list)
    outputs: list[StationIO] = Field(default_factory=list)
    tests: list[TestStep] = Field(default_factory=list)
    cycleTimeSec: float
    takt: Optional[float] = None
    oprNum: Optional[int] = None
    site: Optional[str] = None


class TestResult(BaseModel):
    id: str
    stepId: str
    itemRef: str
    pass_: bool = Field(alias="pass")
    measurements: dict[str, Union[float, str]] = Field(default_factory=dict)
    startedAt: str
    finishedAt: str
    operator: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"populate_by_name": True}
