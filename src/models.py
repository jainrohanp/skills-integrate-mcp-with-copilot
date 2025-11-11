from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    grade: Optional[str]
    is_active: bool = True

class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str]
    schedule: Optional[str]
    max_participants: Optional[int]

class Signup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int
    activity_id: int
    signed_up_at: datetime = Field(default_factory=datetime.utcnow)
