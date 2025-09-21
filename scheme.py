from pydantic import BaseModel, Field
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: str
    
    
class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
    
class User_out(UserLogin):
    id: int 
    
    class Config:
        from_attributes = True
        

# Todo schemas

class TodoBase(BaseModel):
    title: str
    description: str
    pripority: Optional[int] = Field(default=1, ge=1, le=5)
    
class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass

class Todo_out(TodoBase):
    id: int
    owner_id: int
    
    class Config:
        from_attributes = True
        