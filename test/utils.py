from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.schemas.database import data
from app.schemas.model_db import Order, User
import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.routers.user import hash

database = "sqlite:///testdb.sqlite"
engine = create_engine(
    database,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool

)
test_begin = sessionmaker(bind=engine, autocommit=False, autoflush=False)
data.metadata.create_all(bind=engine)


def overide_get_db():
    db = test_begin()
    try:
        yield db

    finally:
        db.close


def overide_get_user():
    return {"username": "Imisioluwa23", "user_id": 1}


client = TestClient(app)


@pytest.fixture
def test_order():
    orderform = Order(
        id=1,
        customer_name="Imisioluwa23",
        customer_order="Pizza",
        checked_out=False,
        price=3.99,
        user_id=1
    )
    db = test_begin()
    db.add(orderform)
    db.commit()
    yield orderform
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM 'order';"))
        connection.commit()


@pytest.fixture
def test_user():
    user = User(
        first_name="Imisioluwa",
        last_name="Isong",
        username="Imisioluwa23",
        email="isongrichard234@gmail.com",
        password=hash.hashed("Imisioluwa234."),
        phone_number="+234-9047-7100-32",
    )

    db = test_begin()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM 'users';"))
        connection.commit()
        print("user table deleted")
