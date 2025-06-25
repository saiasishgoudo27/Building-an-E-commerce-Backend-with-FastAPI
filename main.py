from sqlalchemy import Column, Integer, String
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from Connection import get_db, SessionLocal, engine
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
import Models
from Models import User, Products, Categories, Orders, OrderItems, Cart, Payments
from jwt_auth import get_password_hash, verify_password
from fastapi import Security
from pydantic import constr
from fastapi import Security, Depends, HTTPException, status
from jwt_auth import get_current_active_user_from_bearer as get_current_active_user, verify_password, create_access_token
from datetime import timedelta

app = FastAPI()

Models.base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserBase(BaseModel):
    username: str
    password: str
    email: str
    address: str
    phone: str  # Phone number must be exactly 10 digits
    role: str

# User response
class UserResponse(BaseModel):
    username: str
    email: str
    address: str
    phone: str
    role: str

    class Config:
        orm_mode = True

class ProductsBase(BaseModel):
    prod_name: str
    description: str
    price: int
    stock_quantity: int
    cat_id: int
    image_url: str

# Products response
class ProductResponse(BaseModel):
    prod_name: str
    description: str
    price: int
    stock_quantity: int
    cat_id: int
    image_url: str

    class Config:
        orm_mode = True

class CategoriesBase(BaseModel):
    cat_name: str
    cat_description: str

# Categories response
class CategoriesResponse(BaseModel):
    cat_name: str
    cat_description: str

    class Config:
        orm_mode = True

class OrdersBase(BaseModel):
    order_id: int
    user_id: int
    order_date: datetime
    total_amount: int
    status: str

# Orders response
class OrdersResponse(BaseModel):
    order_id: int
    user_id: int
    order_date: str
    total_amount: int
    status: str

    class Config:
        orm_mode = True

class OrderItemsBase(BaseModel):
    order_id: int
    prod_id: int
    quantity: int
    price: int

# Order items response
class OrdersItemsResponse(BaseModel):
    order_id: int
    prod_id: int
    quantity: int
    price: int

    class Config:
        orm_mode = True

class CartBase(BaseModel):
    user_id: int
    prod_id: int
    quantity: int

# Cart response
class CartResponse(BaseModel):
    user_id: int
    prod_id: int
    quantity: int

    class Config:
        orm_mode = True

class PaymentsBase(BaseModel):
    order_id: int
    payment_method: str
    payment_date: str
    amount: int

# Payments response
class PaymentsResponse(BaseModel):
    order_id: int
    payment_method: str
    payment_date: str
    amount: int

    class Config:
        orm_mode = True

db_dependency = Annotated[Session, Depends(get_db)]

class LoginCredentials(BaseModel):
    username: str
    password: str

@app.post("/login_Form", tags=["Authentication"])
async def login_for_access_token(credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = db.query(Models.User).filter(Models.User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user_profile/", status_code=status.HTTP_200_OK, tags=["Users"])
async def get_users_details(db: db_dependency, current_user=Security(get_current_active_user)):
    if current_user.role == "admin":
        # Return only the current user's details if not admin
        users = db.query(User).all()
        return users
    elif current_user.role == "Customer":
        users = db.query(Models.User).filter(Models.User.id==current_user.id).all()
        return users
    else:
        return {"Message":"You are not privilized to see user details"}

@app.post("/SignUp", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def create_user(user: UserBase, db: db_dependency):
    # Authorization: Only admin can create users
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    existing_user = db.query(Models.User).filter(Models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Username already exists...!!!"])

    existing_email = db.query(Models.User).filter(Models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Email already exists...!!!"])

    hashed_password = get_password_hash(user.password)

    db_user = Models.User(
        username=user.username,
        password=hashed_password,
        email=user.email,
        phone=user.phone,
        address=user.address,
        role=user.role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"Message": "User Profile is Successfully Created..."}

@app.get("/Users_By_id/{id}", status_code=status.HTTP_200_OK, tags=["Users"])
async def users_by_id(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: admin or user himself
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    u1 = db.query(Models.User).filter(Models.User.id == id).first()
    if u1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["User details not Found...!!"])
    return u1

@app.delete("/delete_particular_user/{id}", status_code=status.HTTP_200_OK, tags=["Users"])
async def delete_particular_user(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can delete users

    if current_user.role == "admin" or current_user.id==User.id:
        ud1 = db.query(Models.User).filter(Models.User.id == id).first()
        if ud1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        db.delete(ud1)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Re-sequence User ids and update foreign keys in related tables
    users_to_update = db.query(Models.User).filter(Models.User.id > id).order_by(Models.User.id).all()
    for user in users_to_update:
        old_id = user.id
        new_id = old_id - 1

        # Update foreign keys in Orders, Cart, Payments referencing this user
        orders = db.query(Models.Orders).filter(Models.Orders.user_id == old_id).all()
        for order in orders:
            order.user_id = new_id

        carts = db.query(Models.Cart).filter(Models.Cart.user_id == old_id).all()
        for cart in carts:
            cart.user_id = new_id

        # Update user id
        user.id = new_id

    db.commit()
    return {"Message": "User account deleted and ids re-sequenced..."}

@app.put("/Update_User_profile/{username}", status_code=status.HTTP_200_OK, tags=["Users"])
async def Update_User_detail(username: str, user: UserBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can update users
    if current_user.role == "admin" or current_user.id==User.id:
        db_user = db.query(Models.User).filter(Models.User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        try:
            db_user.email = user.email
            db_user.address = user.address
            db_user.phone = user.phone
            db_user.role = user.role
        # Optionally update password if provided and hashed
            if user.password:
                db_user.password = get_password_hash(user.password)
                db.commit()
                db.refresh(db_user)
                return {"Message": "User Successfully Updated"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@app.get("/Products_details", status_code=status.HTTP_200_OK, tags=["Products"])
async def get_products_details(db: db_dependency, current_user=Security(get_current_active_user)):
    if current_user:
        products = db.query(Models.Products).all()
    return products

@app.post("/Create_Product", status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(product: ProductsBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # breakpoint()
    # Authorization: Only admin can create products
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        existing_product = db.query(Models.Products).filter(Models.Products.prod_name == product.prod_name).first()
        if existing_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists")

        db_product = Models.Products(
            prod_name=product.prod_name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            cat_id=product.cat_id,
            image_url=product.image_url
        )

        db.add(db_product)
        db.commit()
        return {"Message": "Product Successfully Created..."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/Update_Product/{prod_name}", status_code=status.HTTP_200_OK, tags=["Products"])
async def update_product(prod_name: str, product: ProductsBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can update products
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_product = db.query(Models.Products).filter(Models.Products.prod_name == prod_name).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    try:
        db_product.prod_name = product.prod_name
        db_product.description = product.description
        db_product.price = product.price
        db_product.stock_quantity = product.stock_quantity
        db_product.cat_id = product.cat_id
        db_product.image_url = product.image_url
        db.commit()
        db.refresh(db_product)
        return {"Message": "Product Successfully Updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/Delete_particular_product/{prod_name}", status_code=status.HTTP_200_OK, tags=["Products"])
async def delete_particular_product(prod_name: str, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can delete products
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    pd1 = db.query(Models.Products).filter(Models.Products.prod_name == prod_name).first()
    if pd1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prod_id_to_delete = pd1.prod_id
    db.delete(pd1)
    db.commit()

    # Re-sequence Products prod_id and update foreign keys in related tables
    products_to_update = db.query(Models.Products).filter(Models.Products.prod_id > prod_id_to_delete).order_by(Models.Products.prod_id).all()
    for product in products_to_update:
        old_id = product.prod_id
        new_id = old_id - 1

        # Update foreign keys in OrderItems, Cart referencing this product
        order_items = db.query(Models.OrderItems).filter(Models.OrderItems.prod_id == old_id).all()
        for item in order_items:
            item.prod_id = new_id

        carts = db.query(Models.Cart).filter(Models.Cart.prod_id == old_id).all()
        for cart in carts:
            cart.prod_id = new_id

        # Update product id
        product.prod_id = new_id

    db.commit()
    return {"Message": "Product deleted and ids re-sequenced..."}

@app.get("/Product_by_name/{name}", status_code=status.HTTP_200_OK, tags=["Products"])
async def product_by_name(name: str, db: db_dependency):
    p1 = db.query(Models.Products).filter(Models.Products.prod_name == name).first()
    if p1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return p1


@app.get("/Categories_details", status_code=status.HTTP_200_OK, tags=["Categories"])
async def categories_details(db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user:
        categories = db.query(Models.Categories).all()
        return categories

@app.post("/Create_Categories", status_code=status.HTTP_201_CREATED, tags=["Categories"])
async def create_categories(categories: CategoriesBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can create categories
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        existing_categories = db.query(Models.Categories).filter(Models.Categories.cat_name == categories.cat_name).first()
        if existing_categories is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Category already exists..."])

        db_category = Models.Categories(
            cat_name=categories.cat_name,
            cat_description=categories.cat_description
        )

        db.add(db_category)
        db.commit()
        return {"Message": "Category Successfully Created..."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/Categories_by_name/{cat_name}", status_code=status.HTTP_200_OK, tags=["Categories"])
async def categories_by_id(cat_name: str, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user:
        c1 = db.query(Models.Categories).filter(Models.Categories.cat_name == cat_name).first()
        if c1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Category details not Found...!!"])
        return c1

@app.put("/Update_Category/{cat_name}", status_code=status.HTTP_200_OK, tags=["Categories"])
async def update_category(cat_name: str, category: CategoriesBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can update categories
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_category = db.query(Models.Categories).filter(Models.Categories.cat_name == cat_name).first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    try:
        db_category.cat_name = category.cat_name
        db_category.cat_description = category.cat_description
        db.commit()
        db.refresh(db_category)
        return {"Message": "Category Successfully Updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/Delete_particular_category/{cat_name}", status_code=status.HTTP_200_OK, tags=["Categories"])
async def delete_particular_category(cat_name: str, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can delete categories
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        cd1 = db.query(Models.Categories).filter(Models.Categories.cat_name == cat_name).first()
        if cd1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        cat_id_to_delete = cd1.cat_id
        db.delete(cd1)
        db.commit()

        # Re-sequence Categories cat_id (not autoincrement) and update foreign keys in Products referencing this category
        categories_to_update = db.query(Models.Categories).filter(Models.Categories.cat_id > cat_id_to_delete).order_by(Models.Categories.cat_id).all()
        for category in categories_to_update:
            old_id = category.cat_id
            new_id = old_id - 1

            products = db.query(Models.Products).filter(Models.Products.cat_id == old_id).all()
            for product in products:
                product.cat_id = new_id

            category.cat_id = new_id

        db.commit()
        return {"Message": "Category deleted and ids re-sequenced..."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/Orders_details", status_code=status.HTTP_200_OK, tags=["Orders"])
async def order_details(db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins are not authorized to create orders")
    if current_user:
        orders = db.query(Models.Orders).filter(Models.Orders.id==current_user.id).all()
        return orders
    else:
        return {"Message":"You are not privilized to see OrderItems details"}

@app.post("/Create_Order", status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(order: OrdersBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only non-admin user can create orders for themselves
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins are not authorized to create orders")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only create orders for yourself")
    existing_order = db.query(Models.Orders).filter(Models.Orders.id == order.order_id).first()
    if existing_order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Order already exists..."])
    db_order = Models.Orders(
        user_id=order.user_id,
        order_date=order.order_date,
        total_amount=order.total_amount,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    return {"Message": "Order Successfully Created..."}

@app.get("/Orders_by_id/{id}", status_code=status.HTTP_200_OK, tags=["Orders"])
async def orders_by_id(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    o1 = db.query(Models.Orders).filter(Models.Orders.id == id,Models.Orders.id==current_user.id).first()
    if o1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Order details not Found...!!"])
    return o1

@app.delete("/delete_particular_order/{id}", status_code=status.HTTP_200_OK, tags=["Orders"])
async def delete_particular_order(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can delete orders
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    od1 = db.query(Models.Orders).filter(Models.Orders.id == id,Models.Orders.id==current_user.id).first()
    if od1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(od1)
    db.commit()

    # Re-sequence Orders id and update foreign keys in OrderItems, Payments referencing this order
    orders_to_update = db.query(Models.Orders).filter(Models.Orders.id > id).order_by(Models.Orders.id).all()
    for order in orders_to_update:
        old_id = order.id
        new_id = old_id - 1
        order_items = db.query(Models.OrderItems).filter(Models.OrderItems.order_id == old_id).all()
        for item in order_items:
            item.order_id = new_id
        payments = db.query(Models.Payments).filter(Models.Payments.order_id == old_id).all()
        for payment in payments:
            payment.order_id = new_id
        order.id = new_id
    db.commit()
    return {"Message": "Order deleted and ids re-sequenced..."}


@app.get("/OrderItems_details", status_code=status.HTTP_200_OK, tags=["OrderItems"])
async def order_items_details(db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Access to admin")
    if current_user:
        order_items = db.query(Models.OrderItems).filter(Models.OrderItems.id==current_user.id).all()
        return order_items
    else:
        return {"Message":"You are not privilized to see OrderItems details"}

@app.post("/Create_OrderItems", status_code=status.HTTP_201_CREATED, tags=["OrderItems"])
async def create_order_items(orderitems: OrderItemsBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can create order items
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    try:
        existing_orderitems = db.query(Models.OrderItems).filter(Models.OrderItems.order_id == orderitems.order_id,Models.OrderItems.id==current_user.id).first()
        if existing_orderitems:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Order items already exists..."])

        # Check if order exists
        order = db.query(Models.Orders).filter(Models.Orders.id == orderitems.order_id).first()
        if order is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order does not exist")

        db_orderitems = Models.OrderItems(
            order_id=orderitems.order_id,
            prod_id=orderitems.prod_id,
            quantity=orderitems.quantity,
            price=orderitems.price
        )
        db.add(db_orderitems)
        db.commit()
        db.refresh(db_orderitems)
        return {"Message": "Successfully Created..."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/OrderItems_by_id/{id}", status_code=status.HTTP_200_OK, tags=["OrderItems"])
async def order_items_by_id(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can access
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    oi1 = db.query(Models.OrderItems).filter(Models.OrderItems.id == id,Models.OrderItems.id==current_user.id).first()
    if oi1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Order items details not Found...!!"])
    return oi1

@app.delete("/Delete_particular_orderitems/{id}", status_code=status.HTTP_200_OK, tags=["OrderItems"])
async def delete_particular_order_items(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can delete order items
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    oid1 = db.query(Models.OrderItems).filter(Models.OrderItems.id == id,Models.OrderItems.id==current_user.id).first()
    if oid1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(oid1)
    db.commit()

    # Re-sequence OrderItems id
    order_items_to_update = db.query(Models.OrderItems).filter(Models.OrderItems.id > id).order_by(Models.OrderItems.id).all()
    for item in order_items_to_update:
        old_id = item.id
        new_id = old_id - 1
        item.id = new_id

    db.commit()
    return {"Message": "Order items deleted and ids re-sequenced..."}

@app.put("/Update_OrderItems/{id}", status_code=status.HTTP_200_OK, tags=["OrderItems"])
async def update_order_items(id: int, orderitems: OrderItemsBase, db: db_dependency, current_user=Security(get_current_active_user)):
    # Authorization: Only admin can update order items
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_orderitems = db.query(Models.OrderItems).filter(Models.OrderItems.id == id,Models.OrderItems.id==current_user.id).first()
    if db_orderitems is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order items not found")
    try:
        db_orderitems.order_id = orderitems.order_id
        db_orderitems.prod_id = orderitems.prod_id
        db_orderitems.quantity = orderitems.quantity
        db_orderitems.price = orderitems.price
        db.commit()
        db.refresh(db_orderitems)
        return {"Message": "Order items Successfully Updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/Cart_details", status_code=status.HTTP_200_OK, tags=["Cart"])
async def cart_details(db: db_dependency,current_user=Security(get_current_active_user)):
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="No Access to admin.")
    if current_user: 
        cart_deatils = db.query(Models.Cart).filter(Models.Cart.user_id==current_user.id).all()
        return cart_deatils
    else:
        return {"Message":"You are not privilized to see cart details"}

@app.post("/Create_Cart", status_code=status.HTTP_201_CREATED, tags=["Cart"])
async def create_cart(cart: CartBase, db: db_dependency,current_user=Security(get_current_active_user)):
    if current_user.role=="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=["No Access to admin...!"])
    if cart.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=["Access only to the verified user...!"])
    
    db_cart = Models.Cart(
        user_id=cart.user_id,
        prod_id=cart.prod_id,
        quantity=cart.quantity
    )
    db.add(db_cart)
    db.commit()
    return {"Message": "Successfully Created..."}

@app.get("/Cart_by_id/{id}", status_code=status.HTTP_200_OK, tags=["Cart"])
async def cart_by_id(id: int, db: db_dependency, current_user=Security(get_current_active_user)):
    if current_user.role == 'admin':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Only Current user has cart access')
    c1 = db.query(Models.Cart).filter(Models.Cart.id == id, Models.Cart.user_id == current_user.id).first()
    if not c1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Cart details not Found...!!"])
    return c1

@app.delete("/Delete_particular_cart/{id}", status_code=status.HTTP_200_OK, tags=["Cart"])
async def delete_particular_cart(id: int, db: db_dependency,current_user=Security(get_current_active_user)):
    if current_user.role=='admin':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Only Current user has cart access')
    cd1 = db.query(Models.Cart).filter(Models.Cart.id == id,Models.Cart.id==current_user.id).first()
    if cd1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(cd1)
    db.commit()

    # Re-sequence Cart id
    carts_to_update = db.query(Models.Cart).filter(Models.Cart.id > id).order_by(Models.Cart.id).all()
    for cart in carts_to_update:
        old_id = cart.id
        new_id = old_id - 1
        cart.id = new_id

    db.commit()
    return {"Message": "Cart deleted and ids re-sequenced..."}

@app.put("/Update_Cart/{id}", status_code=status.HTTP_200_OK, tags=["Cart"])
async def update_cart(id: int, cart: CartBase, db: db_dependency,current_user=Security(get_current_active_user)):
    if current_user.role=='admin':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Only Current user has cart access')
    db_cart = db.query(Models.Cart).filter(Models.Cart.id == id,Models.Cart.id==current_user.id).first()
    if db_cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    try:
        db_cart.user_id = cart.user_id
        db_cart.prod_id = cart.prod_id
        db_cart.quantity = cart.quantity
        db.commit()
        db.refresh(db_cart)
        return {"Message": "Cart Successfully Updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

