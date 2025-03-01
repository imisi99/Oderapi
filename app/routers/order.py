from fastapi import APIRouter, Depends, HTTPException, Path, Request
from typing import Annotated
from pydantic import BaseModel, Field
from ..schemas.database import engine, begin
from ..schemas import model_db as model_db
from ..schemas.model_db import Order
from .user import GetUser
from starlette import status
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

order = APIRouter()
model_db.data.metadata.create_all(bind=engine)
template = Jinja2Templates(directory="app/templates")


def get_db():
    db = begin()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[str, Depends(GetUser)]


class OrderForm(BaseModel):
    customer_order: str = Field
    price: float = Field(gt=0, example=0)
    checked_out: Annotated[bool, Field(default=False)]

    class Config:
        json_schema_extra = {
            "example": {
                "customer_order": "order",
                "price": 0.00

            }
        }


@order.get("/test")
async def test(request: Request):
    return template.TemplateResponse("login.html", {"request": request})


# Get all order in db
@order.get("/", status_code=status.HTTP_200_OK,
           response_description={200: {"description": "Getting all of user order"}})
async def get_all_orders(db: db_dependency, user: user_dependency):
    return db.query(Order).filter(Order.user_id == user.get("user_id")).all()


# Get order by id
@order.get("/{order_id}", status_code=status.HTTP_200_OK,
           response_description={200: {"description": "Getting order by order_id"}})
async def get_order_id(db: db_dependency, user: user_dependency, order_id: int = Path(gt=0)):
    order_data = db.query(Order).filter(Order.id == order_id).filter(Order.user_id == user.get("user_id")).first()
    if order_data is not None:
        return order_data
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


# Create an Order
@order.post("/create", status_code=status.HTTP_201_CREATED,
            response_description={201: {"description": "User has successfully created an order"}})
async def create_order(db: db_dependency, user: user_dependency, order: OrderForm):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    order_created = False
    # order_create = Order(**order.dict())
    order_create = Order(
        customer_name=user.get("username"),
        customer_order=order.customer_order,
        price=order.price,
        checked_out=False,
        user_id=user.get("user_id")
    )

    db.add(order_create)
    db.commit()
    db.refresh(order_create)
    order_created = True

    if not order_created:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return "Order created successfully"


class Checked_out(BaseModel):
    checked_out: Annotated[bool, Field(False)]

    class Config:
        json_schema_extra = {
            'example': {
                'checked_out': False
            }
        }


# Update an Order by checked_out
@order.put("/update/{order_id}", status_code=status.HTTP_202_ACCEPTED,
           response_description={202: {"description": "User has checked out order"}})
async def update_order(db: db_dependency, user: user_dependency,
                       order: Checked_out,
                       order_id: int = Path(gt=0)):
    order_updated = False
    update = db.query(Order).filter(order_id == Order.id).filter(Order.user_id == user.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    if update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Uploading just the checked_out if user has paid

    # update.customer_name = order.customer_name
    # update.customer_order = order.customer_order
    # update.price = order.price
    update.checked_out = order.checked_out

    db.add(update)
    db.commit()
    db.refresh(update)
    order_updated = True
    if not order_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bad Request")

    return "Order has been checked out successfully"


# Delete an order
@order.delete("/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT,
              response_description={204: {"description": "User has  deleted an order"}})
async def delete_order(db: db_dependency, user: user_dependency,
                       order_id: int = Path(gt=0)):
    order_deleted = False
    delete = db.query(Order).filter(order_id == Order.id).filter(Order.user_id == user.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    if delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db.delete(delete)
    db.commit()
    order_deleted = True
    if not order_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return "Order has been deleted"
