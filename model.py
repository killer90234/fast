from sqlalchemy import Integer, String, Column, ForeignKey, Text
from db import base
from sqlalchemy.orm import relationship

class User(base):
    __tablename__ = "Users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(40), unique=True, index=True)
    email = Column(String(40), unique=True, index=True)
    password = Column(String)
    
    todo = relationship("Todo", back_populates="owner")
    
class Todo(base):
    __tablename__ = "Todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(80), index=True)
    description = Column(Text)
    pripority = Column(Integer, default=1)
    
    owner_id = Column(Integer, ForeignKey("Users.id"))
    
    
    owner = relationship("User", back_populates="todo")
    