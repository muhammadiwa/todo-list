from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User models
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Checklist models
class ChecklistBase(BaseModel):
    name: str

class ChecklistCreate(ChecklistBase):
    pass

class Checklist(ChecklistBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Checklist Item models
class ChecklistItemBase(BaseModel):
    itemName: str

class ChecklistItemCreate(ChecklistItemBase):
    pass

class ChecklistItem(ChecklistItemBase):
    id: int
    checklist_id: int
    is_completed: bool
    created_at: datetime

    class Config:
        orm_mode = True
