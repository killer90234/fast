from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model import User, Todo
from util import get_user, verify_password
from db import base, engine, SessionLocal
from sqlalchemy.orm import Session
import scheme
from typing import List
from authlib.jose import jwt, JoseError
from auth import pass_context, verify_password, create_access_token, SC, ALGO


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

base.metadata.create_all(bind=engine)


    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode token
        claims = jwt.decode(token, SC)
        claims.validate()  # raises JoseError if expired or invalid
        username = claims.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from DB
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except JoseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
 
@app.post("/register/")
def register(user: scheme.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    hashed_password = pass_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token({"sub": db_user.username})
    
    return {
        "msg": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    
@app.post('/login/')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    access_token = create_access_token({"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/todo/", response_model=List[scheme.Todo_out])
def all_todo(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    return db.query(Todo).filter(Todo.owner_id == username.id).all()

@app.get("/todo/{t_id}", response_model=scheme.Todo_out)
def get_todo(t_id: int, db: Session =Depends(get_db), username: str =Depends(get_current_user)):
    todo = db.query(Todo).filter(Todo.id == t_id).first()
    if not todo:
        return HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/create-todo/", response_model=scheme.Todo_out)
def create_todo(
    todo: scheme.TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        pripority=todo.pripority,
        owner_id=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.put("/update-todo/{t_id}", response_model=scheme.Todo_out)
def update_todo(t_id: int, todo: scheme.TodoUpdate, db: Session = Depends(get_db), username: str =Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == t_id).first()
    # user = db.query(User).filter(User.username == username).first()
    
    # if user.id != db_todo.owner_id:
    #     raise HTTPException(status_code=403, detail="You are not authorized to update this todo")
    
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.pripority = todo.pripority
        db_todo.owner_id = username.id
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    
@app.delete("/delete-todo/{t_id}", response_model=scheme.Todo_out)
def delete_todo(t_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    
    db_todo = db.query(Todo).filter(Todo.id == t_id).first()
   
    
   
    
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return db_todo
    
    




# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = get_user(form_data.username)
    
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Invaild User")
#     if not verify_password(form_data.password, user_dict['hashed_password']):
#         raise HTTPException(status_code=400, detail="Invaild Password")
    
#     access_token = create_access_token(data={'JAMES-LEE': form_data.username})
#     return {'access_token': access_token, 'token_type': 'bearer'}


# @app.get("/users")
# def read_users(token: str = Depends(oauth2_scheme)):
#     username = verify_token(token)
#     return {'username': username }
