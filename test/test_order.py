from starlette import status
from app.schemas.model_db import Order
from app.routers.order import get_db, GetUser
from .utils import *

app.dependency_overrides[get_db] = overide_get_db
app.dependency_overrides[GetUser] = overide_get_user


def test_read_all_order():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Welcome to the number one food delivery in Nigeria"


def test_get_all_order(test_order):
    response = client.get("/order")
    assert response.status_code == status.HTTP_200_OK
    sorted_response = sorted(response.json(), key=lambda x: x['id'])
    assert sorted_response == [{"id": 1,
                                "customer_name": "Imisioluwa23",
                                "customer_order": "Pizza",
                                "checked_out": False,
                                "price": 3.99,
                                "user_id": 1
                                }]


def test_get_order_id(test_order):
    response = client.get("/order/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1,
                               "customer_name": "Imisioluwa23",
                               "customer_order": "Pizza",
                               "checked_out": False,
                               "price": 3.99,
                               "user_id": 1
                               }


def test_not_found(test_order):
    response = client.get("/order/55")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': "Order not found"}


def test_order_create(test_order):
    form = {
        'customer_name': "Imisioluwa",
        'customer_order': "Chicken",
        'checked_out': False,
        "price": 3.99,
        'user_id': 1
    }

    response = client.post("/order/create", json=form)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == "Order created successfully"


def test_update_order(test_order):
    form = {
        'checked_out': True
    }

    response = client.put("/order/update/1", json=form)
    assert response.status_code == status.HTTP_202_ACCEPTED
    db = test_begin()
    model = db.query(Order).filter(Order.id == 1).first()
    assert model.checked_out == True
    assert response.json() == "Order has been checked out successfully"


# Update failure

def test_update_id(test_order):
    form = {
        'checked_out': True
    }

    response = client.put("/order/update/33", json=form)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    db = test_begin()
    model = db.query(Order).filter(Order.id == 33).first()
    assert model is None
    assert response.json() == {"detail": "Order not found"}


def test_delete_order(test_order):
    response = client.delete("/order/delete/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = test_begin()
    model = db.query(Order).filter(Order.id == 1).first()
    assert model is None


def test_delete_order_wrong(test_order):
    response = client.delete("/order/delete/33")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Order not found"}
