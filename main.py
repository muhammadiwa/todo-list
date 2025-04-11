from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import uvicorn
from database import get_db, Database
import models
import os
from dotenv import load_dotenv

# Initialize FastAPI app
app = FastAPI(title="To-Do List API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
load_dotenv()  # Load environment variables from .env file
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database instance
db = Database()

# Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        return user
    except jwt.PyJWTError:
        raise credentials_exception

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Authentication endpoints
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/register")
async def register(user: models.UserCreate):
    db_user = db.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    db_user = db.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return db.create_user(user)

# Checklist endpoints
@app.get("/api/checklist", response_model=List[models.Checklist])
async def get_all_checklists(current_user: models.User = Depends(get_current_user)):
    return db.get_checklists(current_user.id)

@app.post("/api/checklist", response_model=models.Checklist)
async def create_checklist(
    checklist: models.ChecklistCreate,
    current_user: models.User = Depends(get_current_user)
):
    return db.create_checklist(checklist, current_user.id)

@app.delete("/api/checklist/{checklist_id}")
async def delete_checklist(
    checklist_id: int,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    db.delete_checklist(checklist_id)
    return {"message": "Checklist deleted successfully"}

# Checklist Item endpoints
@app.get("/api/checklist/{checklist_id}/item", response_model=List[models.ChecklistItem])
async def get_checklist_items(
    checklist_id: int,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return db.get_checklist_items(checklist_id)

@app.post("/api/checklist/{checklist_id}/item", response_model=models.ChecklistItem)
async def create_checklist_item(
    checklist_id: int,
    item: models.ChecklistItemCreate,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return db.create_checklist_item(checklist_id, item)

@app.get("/api/checklist/{checklist_id}/item/{item_id}", response_model=models.ChecklistItem)
async def get_checklist_item(
    checklist_id: int,
    item_id: int,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    item = db.get_checklist_item(item_id)
    if not item or item.checklist_id != checklist_id:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/checklist/{checklist_id}/item/{item_id}")
async def update_checklist_item_status(
    checklist_id: int,
    item_id: int,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    item = db.get_checklist_item(item_id)
    if not item or item.checklist_id != checklist_id:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = db.toggle_checklist_item_status(item_id)
    return updated_item

@app.delete("/api/checklist/{checklist_id}/item/{item_id}")
async def delete_checklist_item(
    checklist_id: int,
    item_id: int,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    item = db.get_checklist_item(item_id)
    if not item or item.checklist_id != checklist_id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_checklist_item(item_id)
    return {"message": "Item deleted successfully"}

@app.put("/api/checklist/{checklist_id}/item/rename/{item_id}")
async def rename_checklist_item(
    checklist_id: int,
    item_id: int,
    item: models.ChecklistItemCreate,
    current_user: models.User = Depends(get_current_user)
):
    checklist = db.get_checklist(checklist_id)
    if not checklist or checklist.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Checklist not found")
    existing_item = db.get_checklist_item(item_id)
    if not existing_item or existing_item.checklist_id != checklist_id:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = db.rename_checklist_item(item_id, item.itemName)
    return updated_item

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
