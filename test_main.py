from fastapi.testclient import TestClient
from AltSchool.Orderapi.app.main import app
import pytest
from unittest.mock import patch, MagicMock
from schemas.model_db import Order

client = TestClient(app)

#Mocking the database 
@pytest.fixture()
def mock_db():
    with patch("main.begin") as mocked:
        mocked.return_value = MagicMock()
        yield mocked


#testing a post route 
def test_create_order(mock_db):
    test_order = {
        "customer_name" : "Isong Imisioluwa",
        "customer_order" : "Bread and Quaker oats",
        "price" : "2000",
        "checked_out" : "false"
    }
    
    response = client.post("/order/create", json = test_order)
    assert response.status_code == 200
    assert response.json() == "Order created successfully"

#testing a get all data route 
def test_get_all_order(mock_db):
    mock_db.return_value.query.return_value.all.return_value = [
        Order(id = 1, customer_name = "Isong Imisioluwa", customer_order = "Bread and Beans", price = 1234, checked_out = False),
        Order(id = 2, customer_name = "Isong Imisioluwa", customer_order = "Bread and Beans", price = 1234, checked_out = False)
    ]

    response = client.get("/order")
    assert response.status_code == 200
    assert len(response.json()) == 2

#testing an order with id
def test_get_order_id(mock_db):
    mock_db.return_value.query.return_value.filter.return_value.first.return_value = [
        Order(id = 1, customer_name = "Isong Imisioluwa", customer_order = "Bread and Beans", price = 1234, checked_out = False)
    ]

    response = client.get("/order/5")
    assert response.status_code ==200
    assert response.json()[0]["price"] == 1234

#test to update 
def test_update_order(mock_db):
    updated_order = {
        "customer_name": "Micheal Jackson",
        "customer_order" : "Pepporonni Pizza",
        "price" : 2300,
        "checked_out" : False
    }

    response = client.put("/order/4", json = updated_order)
    assert response.status_code == 200
    assert response.json() == "Order has been checked out successfully"    

#test to delete
def test_delete_order(mock_db):
    response = client.delete("/order/2")
    assert response.status_code == 200
    assert response.json() == "Order has been deleted"