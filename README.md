# 🏗️ E-Commerce Backend with FastAPI

Welcome to my e-commerce backend project powered by **FastAPI** — a modern, high-performance Python framework! This repository showcases a fully functional API with user authentication, product management, cart operations, and order processing.

---

## 🚀 Why FastAPI?

FastAPI is 🔥 for backend development because of:
- ⚡ **High performance** (comparable to Node.js & Go)
- ✅ Built-in validation and docs (Swagger/OpenAPI)
- 🧠 Modern Pythonic syntax with type hints
- 🔄 Support for asynchronous operations

Used by giants like Netflix, Microsoft, Uber, and more 🚀.

---

## 🌟 Features at a Glance

✅ JWT-Based Authentication & Role-Based Access  
🛍️ Product & Category Management (Admin)  
🛒 Cart Operations (Customer)  
📦 Order Placement & Management  
🧑‍💻 Secure User Management  
🔐 Protected Routes using OAuth2 & HTTP Bearer  
🔁 Clean SQLAlchemy DB Relationships  

---

## 🧱 Project Structure

📁 app/
┣ 📄 main.py # Entry point - API routes
┣ 📄 connection.py # DB connection using SQLAlchemy
┣ 📄 models.py # SQLAlchemy models for DB tables
┣ 📄 jwt_auth.py # Authentication logic (JWT tokens, hashing)


---

## 🔄 Project Workflow

### 1. 🧑‍💻 **User Authentication**
- Users register or log in via `/login_Form`
- Passwords are hashed with bcrypt (`passlib`)
- On login, a **JWT token** is issued with role info embedded

### 2. 🔐 **Role-Based Access**
- Middleware functions (`get_current_user`, `get_current_active_user`) decode tokens
- Admins and Customers are allowed access to different routes

### 3. 📦 **Product & Category Management**
- Admins use protected routes to create, update, or delete:
  - Products via `/Create_Product`
  - Categories via `/Create_Categories`

### 4. 🛒 **Cart Operations**
- Customers:
  - Add products to their cart
  - View items via `/Cart_details`
  - Modify quantities or remove items

### 5. 🧾 **Order System**
- Customers can:
  - Place orders from their cart
  - View their order history
- Orders are linked to users and products via foreign keys

### 6. 🧠 **Data Layer**
- Models defined using SQLAlchemy (`models.py`)
- All DB operations use sessions from `SessionLocal()` in `connection.py`
- Relationships managed cleanly to avoid orphaned or inconsistent records

---

## ⚙️ Tech Stack

| Category        | Tools/Libraries                         |
|-----------------|------------------------------------------|
| 🖥️ Backend       | FastAPI, Uvicorn                        |
| 🛢️ Database      | MySQL, SQLAlchemy                       |
| 🔐 Auth          | JWT (python-jose), PassLib (bcrypt)     |
| 🧰 Utilities     | Pydantic, Python-dotenv, Requests       |

---

## 📦 Installation

Clone the repo:

git clone https://github.com/your-username/ecommerce-fastapi.git
cd ecommerce-fastapi

---

## 🛠️ Getting Started

### ✅ Create & Activate a Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

---

## 📦 Install Dependencies
pip install -r requirements.txt

---

## ⚙️ Update .env or Configure Your DB in connection.py
engine = create_engine("mysql+pymysql://username:password@localhost:3306/ecommerce")
🔐 Tip: You can store your DB credentials securely in a .env file and load them using python-dotenv.

---

## 🚀 Run the FastAPI Server
uvicorn main:app --reload
📌 Visit the API Docs
Your FastAPI interactive documentation (Swagger UI) is available at:
http://127.0.0.1:8000/docs

Or, for ReDoc documentation:
http://127.0.0.1:8000/redoc

---

## 🔑 Authentication & Authorization
Login Endpoint:
Use /login_Form to log in and receive a JWT token.

Access Protected Routes:
Use the token in headers as:

Authorization: Bearer <your-token>
Role-Based Access:

Admin routes (e.g., product/category creation)

Customer routes (e.g., cart management, orders)

Each token encodes the user's role and identity, ensuring secure access control.
Unauthorized access is blocked automatically via dependency injection and token validation.


