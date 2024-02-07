from schemas.database import data
from sqlalchemy import Column, Float, Integer, String, Boolean, ForeignKey

class Order(data):
    __tablename__ = "order"

    id = Column(Integer, primary_key = True, index = True)
    customer_name = Column(String(50), nullable = False)
    customer_order = Column(String(500), nullable= False)
    price = Column(Float, nullable = False)
    checked_out = Column(Boolean, default = False)
    user_id = Column(Integer, ForeignKey("user.id"))

    # def __init__(self, customer_name, customer_order, price, checked_out):
    #     self.customer_name = customer_name
    #     self.customer_order = customer_order
    #     self.price = price
    #     self.checked_out =checked_out


class User(data):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True, index= True)
    first_name = Column(String, nullable= False)
    last_name = Column(String, nullable= False)
    email = Column(String, unique = True, nullable= False)
    username = Column(String, unique= True, nullable= False)
    password = Column(String, nullable= False)
    phone_number = Column(String, nullable= False, unique= True)
