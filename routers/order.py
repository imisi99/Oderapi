from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from pydantic import BaseModel, Field
from schemas.database import engine, begin
import schemas.model_db as model_db
from schemas.model_db import Order
from .user import GetUser

order = APIRouter()
model_db.data.metadata.create_all(bind = engine)

def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[str, Depends(get_db)]
user_dependancy = Annotated[str, Depends(GetUser)]

class OrderForm(BaseModel):
    customer_name: str = Field(min_length = 3, max_length = 20)
    customer_order : str 
    price : float = Field(gt = 0)
    checked_out : bool = Field(False)


#Get all order in db
@order.get("/")
async def get_all_orders(db: db_dependency, user : user_dependancy):

    return db.query(Order).filter(Order.user_id == user.get("user_id")).all()


#Get order by id 
@order.get("/{order_id}")
async def get_order_id(order_id : int, db :db_dependency, user : user_dependancy):
    order_data = db.query(Order).filter(Order.id == order_id).filter(Order.user_id == user.get("user_id")).first()
    if order_data is not None:
        return order_data
    else:
        raise HTTPException (status_code=404, detail= "Order not found")
    

#Create an Order
@order.post("/create")
async def create_order( db : db_dependency, user : user_dependancy, order: OrderForm):
    if user is None:
        raise HTTPException(status_code=401, detail= "Unauthorized access")
    
    #order_create = Order(**order.dict())
    order_create = Order(
        customer_name=order.customer_name,
        customer_order=order.customer_order,
        price=order.price,
        checked_out=order.checked_out,
        user_id = user.get("user_id")
    )

    db.add(order_create)
    db.commit()
    db.refresh(order_create)
    return "Order created successfully"
    

#Update an Order by checked_out
@order.put("/{order_id}",status_code= 200)
async def update_order(db : db_dependency, user : user_dependancy,
                        order : OrderForm,
                        order_id : int = Path(gt=0)):
    update = db.query(Order).filter(order_id == Order.id).filter(Order.user_id == user.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code= 401, detail= "Unauthorized access")
    if update is None:
        raise HTTPException(status_code= 404, detail= "Order not found")
    
    # Uploading just the checked_out if user has paid

    # update.customer_name = order.customer_name
    # update.customer_order = order.customer_order
    # update.price = order.price
    update.checked_out = order.checked_out

    db.add(update)
    db.commit()
    db.refresh(update)

    return "Order has been checked out successfully"

#Delete an order 
@order.delete("/{order_id}")
async def delete_order(db : db_dependency, user : user_dependancy,
                       order_id : int = Path(gt=0)):
    delete = db.query(Order).filter(order_id == Order.id).filter(Order.user_id == user.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code= 401, detail= "Unauthorized access")
    if delete is None:
        raise HTTPException(status_code= 404, detail= "Order not found")
    
    db.delete(delete)
    db.commit()


    return "Order has been deleted"