from sqlalchemy import Boolean, String, Integer, Column, Numeric, DateTime
from Connection import base
from sqlalchemy import ForeignKey

class User(base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    address = Column(String(100), nullable=False)
    phone = Column(String(10), nullable=False)
    role = Column(String(20), nullable=False)  # e.g., customer, admin

class Products(base):
    __tablename__ = 'Products'

    prod_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prod_name = Column(String(30), unique=True, index=True, nullable=False)
    description = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    cat_id = Column(Integer, ForeignKey('Categories.cat_id'), nullable=False)
    image_url = Column(String(100), nullable=True)

class Categories(base):
    __tablename__ = 'Categories'

    cat_id = Column(Integer, primary_key=True, index=True)
    cat_name = Column(String(30), unique=True, index=True, nullable=False)
    cat_description = Column(String(100), nullable=True)

class Orders(base):
    __tablename__ = 'Orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    order_date = Column(DateTime, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # e.g., pending, shipped, delivered

class OrderItems(base):
    __tablename__ = 'OrderItems'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    prod_id = Column(Integer, ForeignKey('Products.prod_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # price at the time of order

class Cart(base):
    __tablename__ = 'Cart'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    prod_id = Column(Integer, ForeignKey('Products.prod_id'), nullable=False)
    quantity = Column(Integer, nullable=False)

class Payments(base):
    __tablename__ = 'Payments'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String(20), nullable=False)  # e.g., credit card, PayPal
    status = Column(String(20), nullable=False)  # e.g., completed, pending, failed
