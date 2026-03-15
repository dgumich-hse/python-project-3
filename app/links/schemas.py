from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    clicks_count: int

class LinkStats(BaseModel):
    original_url: str
    created_at: datetime
    clicks_count: int
    last_used_at: Optional[datetime]

class LinkUpdate(BaseModel):
    original_url: Optional[str]
    expires_at: Optional[datetime]


class LinkCreateUnauthorized(BaseModel):
    original_url: str