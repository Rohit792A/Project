from datetime import timedelta, datetime
import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import get_db
import models
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from jwt import ExpiredSignatureError

router = APIRouter(
    prefix = "/auth",
    tags= ["auth"]
)

SECRET_KEY = "MyKey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/token")

templates = Jinja2Templates(directory="..\\frontend\\templates")


class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str


db_dependency = Annotated[Session, Depends(get_db)]

current_user_role =""

start_time = 0

# Set the expiration time (in seconds)
EXP_TIME = 30000  # For example, 1 hour

# return role of the current user if the session has not expired
def get_user():
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > EXP_TIME:
        return " "
        
    return current_user_role

@router.post("/newtoken", response_model=None)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail= " could not validate user")
    
    token = create_access_token(user.name, user.id, user.user_type, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    global current_user_role
    current_user_role = token
    global start_time
    start_time = time.time()
    return {"access_token": token, "token_type": "bearer", "role": user.user_type}



def authenticate_user(username: str, password: str, db):
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": user_role}
    expires = datetime.now() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(get_user)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        
        if username is None or user_id is None:
            # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            #                     detail="could not validate user")
            return None
        return {"username": username, "id": user_id, "user_type":user_role}
    except JWTError:
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        #                     detail="could not validate user")
        return None
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired")
        # return None

@router.post("/logout")
async def logout():
    global current_user_role
    current_user_role = ""
    return {"message": "logout successful"}







