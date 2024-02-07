from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette import status
from fastapi.testclient import TestClient
from schemas.model_db import Order
from routers.order import get_db, OrderForm
from routers.user import GetUser
from schemas.database import data
import main
from pytest import fixture
import pytest

database = "sqlite:///.testdb.sqlite"
engine = create_engine(
    database,
    connect_args= {"check_same_thread" : False},
    poolclass= StaticPool,

)
begin = sessionmaker(bind= engine, autocommit = False, autoflush = False)
data.metadata.create_all(bind=engine)

def overide_get_db():
    db = begin()
    try:
        yield db 
    finally:
        db.close


def overide_get_user():
    return {"username" : "Imisioluwa23", "user_id" : 1}

main.app.dependency_overrides[get_db] = overide_get_db
main.app.dependency_overrides[GetUser] = overide_get_user

client = TestClient(main.app)

def test_read_all_order():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Welcome to the number one food delivery in Nigeria"

@pytest.fixture()
orderform = Order(
    id = 1,
    customer_name = "Imsioluwa",
    customer_order = "Pizza",
    checked_out = False,
    price = 3.99,
    user_id = 1
)

def test_create_order(orderform):
    response = client.post("/order/create")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == "Order created successfully"
