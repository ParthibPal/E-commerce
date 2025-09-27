from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize PyMongo in your app.py
# mongo = PyMongo(app)

# ============================== PRODUCT ==============================
class Product:
    def __init__(self, mongo, data=None):
        self.collection = mongo.db.products
        if data:
            self.__dict__.update(data)

    def create(self, name, description, price, image, category):
        result = self.collection.insert_one({
            "name": name,
            "description": description,
            "price": price,
            "image": image,
            "category": category,
            "created_at": datetime.utcnow()
        })
        return str(result.inserted_id)

    def get_all(self):
        return list(self.collection.find())

    def get_by_id(self, product_id):
        return self.collection.find_one({"_id": ObjectId(product_id)})

    def to_dict(self, data):
        data["id"] = str(data["_id"])
        return data

# ============================== CART ==============================
class Cart:
    def __init__(self, mongo):
        self.collection = mongo.db.carts

    def add_item(self, user_id, product, quantity=1):
        item = {
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product["_id"]),
            "product_name": product["name"],
            "product_image": product["image"],
            "product_description": product["description"],
            "product_price": product["price"],
            "quantity": quantity,
            "added_at": datetime.utcnow()
        }
        result = self.collection.insert_one(item)
        return str(result.inserted_id)

    def get_user_cart(self, user_id):
        return list(self.collection.find({"user_id": ObjectId(user_id)}))

    def remove_item(self, cart_id):
        self.collection.delete_one({"_id": ObjectId(cart_id)})

    def update_quantity(self, cart_id, quantity):
        self.collection.update_one(
            {"_id": ObjectId(cart_id)},
            {"$set": {"quantity": quantity}}
        )

# ============================== ORDER ==============================
class Order:
    def __init__(self, mongo):
        self.collection = mongo.db.orders

    def create_order(self, user_id, product, quantity):
        order = {
            "user_id": ObjectId(user_id),
            "product_name": product["product_name"],
            "product_image": product["product_image"],
            "product_description": product["product_description"],
            "product_price": product["product_price"],
            "quantity": quantity,
            "ordered_at": datetime.utcnow()
        }
        result = self.collection.insert_one(order)
        return str(result.inserted_id)

    def get_user_orders(self, user_id):
        return list(self.collection.find({"user_id": ObjectId(user_id)}))

# ============================== REVIEW ==============================
class Review:
    def __init__(self, mongo):
        self.collection = mongo.db.reviews

    def add_review(self, user_id, product_id, content, rating):
        review = {
            "user_id": ObjectId(user_id),
            "product_id": ObjectId(product_id),
            "content": content,
            "rating": rating,
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(review)
        return str(result.inserted_id)

    def get_product_reviews(self, product_id):
        return list(self.collection.find({"product_id": ObjectId(product_id)}))

# ============================== USER ==============================
class User:
    def __init__(self, mongo):
        self.collection = mongo.db.users

    def create_user(self, username, email, password):
        hashed_pw = generate_password_hash(password)
        result = self.collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        })
        return str(result.inserted_id)

    def authenticate(self, email, password):
        user = self.collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return user
        return None

# ============================== ADMIN ==============================
class Admin:
    def __init__(self, mongo):
        self.collection = mongo.db.admins

    def create_admin(self, username, password):
        hashed_pw = generate_password_hash(password)
        result = self.collection.insert_one({
            "username": username,
            "password": hashed_pw
        })
        return str(result.inserted_id)

    def authenticate(self, username, password):
        admin = self.collection.find_one({"username": username})
        if admin and check_password_hash(admin["password"], password):
            return admin
        return None
