from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

InteractionLevel = Literal["intentional", "incidental", "none"]


class Persona(BaseModel):
    id: str
    name: str
    role: str
    interactionLevel: InteractionLevel
    goals: list[str] = Field(default_factory=list)
    pains: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    motivationalDrivers: Optional[list[str]] = None
    knowledge: Optional[list[str]] = None
    workhours: Optional[str] = None
