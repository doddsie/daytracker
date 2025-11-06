from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class DiaryBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "My day"})
    content: str = Field(..., json_schema_extra={"example": "Today I wrote code..."})
    tags: List[str] = Field(default_factory=list)
    entry_date: date = Field(..., json_schema_extra={"example": "2025-10-31"})


class DiaryCreate(DiaryBase):
    pass


class DiaryUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]
    entry_date: Optional[date]


class DiaryInDB(DiaryBase):
    id: str
    rev: Optional[str]


class DiaryOut(DiaryInDB):
    pass
