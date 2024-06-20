from fastapi import FastAPI
from .routers.order import order
from .routers.user import user
from starlette.staticfiles import StaticFiles
import os

base = os.path.dirname(os.path.abspath(__file__))
static = os.path.join(base, 'static')

app = FastAPI()
app.include_router(order, prefix="/order", tags=["Order"])
app.include_router(user, prefix="/user", tags=["User"])
app.mount("/app/static", StaticFiles(directory=static), name="static")


@app.get("/")
async def order_home():
    return "Welcome to the number one food delivery in Nigeria"
