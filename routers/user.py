from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import  Annotated
from passlib.context import CryptContext
from schemas.database import engine, begin
import schemas.model_db as model_db
from schemas.model_db import User
from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime
from starlette.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError


user = APIRouter()

#Initializing the db
model_db.data.metadata.create_all(bind = engine)
def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[str, Depends(get_db)]

class UserDetails(BaseModel):
    firstname : str
    lastname : str
    username : str
    email : str
#Hashing the password
hash = CryptContext(schemes=["bcrypt"], deprecated= "auto")

#Authentication and Authorization Logic
def Autentication(username : str , password : str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    password = hash.verify(password, user.password)
    if not password:
        return False
    return user

secret = "272223"
algorithm = "HS256"

def access(username : str, user_id : int , expire : timedelta):
    encode = {"sub": username, "id" : user_id}
    expired = datetime.utcnow() + expire
    encode.update({"expired" : expired.isoformat()})
    return jwt.encode(encode, secret, algorithm= algorithm)

#to collect the token
bearer = OAuth2PasswordBearer(tokenUrl="user/login")

#to get the user with token
async def GetUser(token : Annotated[str, Depends(bearer)]):
    try:
        payload = jwt.decode(token, secret, algorithms= [algorithm])
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code= 401, detail= "Unauthorized Acess")
        return {
            "username" : username,
            "user_id" : user_id
        }
        
    except JWTError:
        raise HTTPException(status_code= 401, detail= "Unautorized acess")
    
user_dependancy = Annotated[str, Depends(GetUser)]
class UserForm(BaseModel):
    first_name : str = Field(min_length=3)
    last_name : str = Field(min_length= 3)
    email : str 
    username : str = Field(min_length= 3)
    password : str

#User signup route 
@user.post("/signup")
async def user_signup(user : UserForm, db : db_dependency):

    existing_username = db.query(User).filter((User.username == user.username)).first()
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_username:
        raise HTTPException(status_code= 400, detail= "username is already in use")
    
    if existing_email:
        raise HTTPException(status_code= 400, detail= "email is already in use")
    user_model = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        username = user.username,
        password = hash.hash(user.password)

    )
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return "User has been created successfully."

#User login route
@user.post("/login")
async def user_login(form : Annotated[OAuth2PasswordRequestForm, Depends()], db :db_dependency):
    user = Autentication(form.username, form.password, db)
    
    

    if not user:
        raise HTTPException(status_code= 401, detail= "Unauthorized access")
    token = access(user.username, user.id, timedelta(minutes=2))
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }

#Changing the user password 
@user.put("/password/recovery")
async def forgot_password(db: db_dependency, username : str, new_password : str ):
    access = db.query(User).filter(username == User.username).first()
    if access is None:
        raise HTTPException(status_code= 401, detail= "Invalid Username")
    
    password = hash.hash(new_password)
    #access.password = user.password
    access.password = password
    db.add(access)
    db.commit()
    db.refresh(access)

    return "Your password has been changed"

#To get logged in user details
@user.get("/details")
async def get_user_details(db : db_dependency, user : user_dependancy ):
    access = db.query(User).filter(User.username == user.get("username")).first()

    if access is not None:
        data = UserDetails(
            firstname= access.first_name,
            lastname= access.last_name,
            username= access.username,
            email= access.email
        )
        return data
    raise HTTPException(status_code= 404, detail= "User details not found")

#Update the current user details 
@user.put("/update")
async def update_details(db : db_dependency, user : user_dependancy, new_data : UserForm):
    access = db.query(User).filter(User.username == user.get("username")).first()
    if access is None:
        raise HTTPException(status_code=404, detail= "Error: Invalid login credentials")
    

    existing_username = db.query(User).filter(User.username == new_data.username).first()
    if existing_username is not None and existing_username.username != user.get("username"):
        raise HTTPException(status_code= 400, detail= "Username is already in use")
    

    existing_email = db.query(User).filter(User.email == new_data.email).first()
    if existing_email is not None and existing_email.email != user.get("email"):
        raise HTTPException(status_code= 400 , detail= "Email is already in use")
    

    access.first_name = new_data.first_name
    access.last_name = new_data.last_name
    access.email = new_data.email
    access.username = new_data.username
    access.password = hash.hash(new_data.password)

    

    db.add(access)
    db.commit()
    db.refresh(access)
    return "Details has been updated succesfully"   
   

#Delete current user
@user.delete("/delete")
async def delete_user(db : db_dependency, user : user_dependancy):
    if user is None:
        raise HTTPException(status_code= 401, detail= "Invalid credentials")
    access = db.query(User).filter(User.username == user.get("username")).first()
    if access is None:
        raise HTTPException(status_code= 404, detail= "Error : User does not exist")
    
    db.delete(access)
    db.commit()
    return "User has been deleted successfully"
