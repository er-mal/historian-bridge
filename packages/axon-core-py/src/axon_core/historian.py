from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

Quality = Literal["good", "bad", "questionable", "uncertain"]


class HistorianTag(BaseModel):
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    assetPath: Optional[str] = None


class HistorianPoint(BaseModel):
    tag: str
    ts: str
    value: float
    quality: Optional[Quality] = None


class TagQuery(BaseModel):
    """Wire/Python TagQuery. Wire field is `from`; Python attribute is `from_`.

    Both `TagQuery(from_=...)` and `TagQuery.model_validate({"from": ...})` work.
    """

    tags: list[str]
    from_: str = Field(alias="from")
    to: str
    agg: Optional[Literal["raw", "avg", "min", "max", "stddev", "count", "first", "last"]] = "raw"
    interval: Optional[str] = None

    model_config = {"populate_by_name": True}
