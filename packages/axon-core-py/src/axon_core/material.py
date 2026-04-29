from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

MaterialCategory = Literal[
    "cathode-active", "anode-active", "electrolyte", "binder",
    "conductive-additive", "current-collector-foil", "separator",
    "tab", "can", "cap", "busbar", "thermal-interface", "adhesive",
    "fastener", "harness", "sensor", "cell", "module", "pack",
    "consumable", "other",
]


class Quantity(BaseModel):
    value: float
    unit: str


class SpecRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    lt: Optional[float] = None
    gt: Optional[float] = None
    unit: str


class MaterialSpec(BaseModel):
    parameters: dict[str, SpecRange] = Field(default_factory=dict)


class Material(BaseModel):
    id: str
    name: str
    category: MaterialCategory
    spec: Optional[MaterialSpec] = None
    countryOfOrigin: Optional[str] = None
    hazardClass: Optional[str] = None


class Supplier(BaseModel):
    id: str
    name: str
    approved: bool = False
    rating: Optional[Literal[1, 2, 3, 4, 5]] = None
