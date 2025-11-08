from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class DiaryBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "My day"})
    content: str = Field(..., json_schema_extra={"example": "Today I wrote code..."})
    tags: List[str] = Field(default_factory=list)


class DiaryCreate(DiaryBase):
    """Input model for creating entries. `entry_date` is set by the server."""
    pass


class DiaryUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]


class DiaryInDB(DiaryBase):
    id: str
    rev: Optional[str]
    entry_date: datetime


class DiaryOut(DiaryInDB):
    pass
