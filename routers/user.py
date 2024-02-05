from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr, validator
from typing import  Annotated
from passlib.context import CryptContext
from schemas.database import engine, begin
import schemas.model_db as model_db
from schemas.model_db import User, Order
from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime
from starlette.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
import re
from starlette import status
from sqlalchemy.orm import Session

user = APIRouter()

#Initializing the db
model_db.data.metadata.create_all(bind = engine)

def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session , Depends(get_db)]

class UserDetails(BaseModel):
    firstname : str
    lastname : str
    username : str
    email : str
    phone_number :str

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

def access(username : str, user_id : int , timedelta):
    encode = {"sub": username, "id" : user_id}
    expired = datetime.utcnow() + timedelta
    encode.update({"exp" : expired})
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
            raise HTTPException(status_code= 401, detail= "Unauthorized Access")
        return {
            "username" : username,
            "user_id" : user_id
        }
        
    except JWTError as e:
        print(f"JWTError occurred: {e}")
        raise HTTPException(status_code= 401, detail= "Unautorized access")
    
user_dependancy = Annotated[str, Depends(GetUser)]


#User form pydantic validation 
class UserForm(BaseModel):
    first_name : str = Field(min_length=3)
    last_name : str = Field(min_length= 3)
    email : EmailStr
    username : str = Field()
    password : str = Field(min_length= 8,description= "Password must contain at least 8 characters, one uppercase letter, and one special character.")
    phone_number : str = Field()

    @validator("password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must have at least one uppercase character")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must have at least one special character")

        return value
    
    @validator("username")
    def check_username(cls, value):
        if len(value) < 3 :
            raise ValueError("Username must be at least 3 characters long")

        return value
    
    class Config():
        json_schema_extra = {
            'example' : {
                'first_name' : 'firstname',
                'last_name' : 'lastname',
                'username' : 'username',
                'email' : 'email@gmail.com',
                'password' : 'password',
                'phone_number' : "+123-4567-8912-34"
            }
        }

#User signup route 
@user.post("/signup", status_code= status.HTTP_201_CREATED)
async def user_signup(user : UserForm, db : db_dependency):
    user_created =False
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
        password = hash.hash(user.password),
        phone_number = user.phone_number

    )
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    user_created = True

    if not user_created:
        raise HTTPException(status_code= 400, detail= "Bad Request")
    

    return "User has been created successfully."

#User login route
@user.post("/login", status_code= status.HTTP_202_ACCEPTED)
async def user_login(form : Annotated[OAuth2PasswordRequestForm, Depends()], db :db_dependency):
    user = Autentication(form.username, form.password, db)
    if not user:
        raise HTTPException(status_code= 401, detail= "Unauthorized access")
    
    token = access(user.username, user.id, timedelta(minutes=2))
    if not token:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Error in trying to log you in please try again later")
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }

#Changing the user password 
class new_form(BaseModel):
    password : str
    confirm_password : str

    @validator("password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 character long")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one upper-case character")
        if not re.search(r'[!@#$%^&*(),.?:{}|<>]', value):
            raise ValueError("Password must contain at least one special character")
            
        return value
    
    
    class Config():
        json_schema_extra = {
            'example' : {
                "password" : "new-password",
                "confirm_password" : "comfirm_password"
            }
        }

      
            
@user.put("/password/recovery",status_code= status.HTTP_202_ACCEPTED)
async def forgot_password(db: db_dependency, username :str, email : str, phone_number : str, new_password : new_form):
    user_password = False
    access = db.query(User).filter(email == User.email).filter(username ==User.username).filter(User.phone_number == phone_number).first()
    if access is None:
        raise HTTPException(status_code= 401, detail= "Invalid Credentials!")
    
    if new_password.password != new_password.confirm_password:
        raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY, detail= "Password does not match")
    
    passcode = hash.hash(new_password.password)
    #access.password = user.password
    access.password = passcode
    db.add(access)
    db.commit()
    db.refresh(access)

    user_password = True

    if not user_password:
        raise HTTPException(status_code= 400, detail= "Bad Request")
    
    return "Your password has been changed successfully"

#To get logged in user details
@user.get("/details", status_code= status.HTTP_200_OK)
async def get_user_details(db : db_dependency, user : user_dependancy ):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    access = db.query(User).filter(User.id == user.get("user_id")).first()

    if access is not None:
        data = UserDetails(
            firstname= access.first_name,
            lastname= access.last_name,
            username= access.username,
            email= access.email,
            phone_number = access.phone_number
        )

        return data
    
    raise HTTPException(status_code= 404, detail= "User details not found")

#Update the current user details 
@user.put("/update-details", status_code= status.HTTP_202_ACCEPTED)
async def update_details(db : db_dependency, user : user_dependancy, new_data : UserForm):
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Unauthorized user")
    
    user_update = False
    access = db.query(User).filter(User.username == user.get("username")).first()
    if access is None:
        raise HTTPException(status_code=404, detail= "Error: Invalid login credentials")
    

    existing_username = db.query(User).filter(User.username == new_data.username).first()
    if existing_username is not None and existing_username.username != access.username:
        raise HTTPException(status_code= 400, detail= "Username is already in use")
    

    existing_email = db.query(User).filter(User.email == new_data.email).first()
    if existing_email is not None and existing_email.email != access.email:
        raise HTTPException(status_code= 400 , detail= "Email is already in use")
    

    access.first_name = new_data.first_name
    access.last_name = new_data.last_name
    access.email = new_data.email
    access.username = new_data.username
    access.phone_number = new_data.phone_number
    access.password = hash.hash(new_data.password)

    

    db.add(access)
    db.commit()
    db.refresh(access)

    user_update = True

    if not user_update:
        raise HTTPException(status_code= 400, detail= "Bad Request")
    
    return "Details has been updated succesfully"   



#Delete current user
@user.delete("/delete-user",status_code= status.HTTP_204_NO_CONTENT)
async def delete_user(db : db_dependency, user : user_dependancy):
    user_deleted = False

    if user is None:
        raise HTTPException(status_code= 401, detail= "Invalid credentials")
    access = db.query(User).filter(User.username == user.get("username")).first()
    order = db.query(Order).filter(Order.user_id == user.get("user_id")).delete()
    if access is None:
        raise HTTPException(status_code= 404, detail= "Error : User does not exist")
    
    if order is None:
        pass
    
    db.delete(access)
    db.commit()
    user_deleted = True
    if not user_deleted:
        raise HTTPException(status_code= 400, detail= "Bad Request")
    
    return "User has been deleted successfully"


