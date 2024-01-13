from fastapi import FastAPI
from routers.order import order 
from routers.user import user

app = FastAPI()
app.include_router(order, prefix="/order", tags=["Order"])
app.include_router(user, prefix= "/user", tags= ["User"])

@app.get("/")
async def order_home():
    return "Welcome to the number one food delivery in Nigeria"