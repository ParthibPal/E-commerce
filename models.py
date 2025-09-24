# Importing required libraries and modules
from flask_sqlalchemy import SQLAlchemy    # For database management with SQLAlchemy ORM
from flask_login import UserMixin          # Provides default implementation for user authentication
from datetime import datetime              # To track when records were created or updated

# Initialize SQLAlchemy instance which will be tied to our Flask app later
db = SQLAlchemy()

# ============================== USER MODEL ==============================
# This model represents the users who will register and log in to the system
class User(db.Model, UserMixin):  
    # 'UserMixin' provides Flask-Login methods like is_authenticated, is_active, etc.
    
    id = db.Column(db.Integer, primary_key=True)  
    # Primary key - uniquely identifies each user

    username = db.Column(db.String(50), unique=True, nullable=False)
    # Unique username for each user, cannot be NULL

    email = db.Column(db.String(120), unique=True, nullable=False)
    # Unique email address, required for login and communication

    password = db.Column(db.String(200), nullable=False)
    # Stores hashed password (not plain text for security reasons)

    is_admin = db.Column(db.Boolean, default=False)
    # Flag to check if the user is an admin, default is False (normal user)

    reviews = db.relationship('Review', back_populates='user', lazy=True)
    # Relationship to Review model:
    #   - 'back_populates' creates a two-way link between User and Review
    #   - A user can have multiple reviews

# ============================== PRODUCT MODEL ==============================
class Product(db.Model):
    __tablename__ = 'product'  # Explicitly naming the database table as 'product'

    id = db.Column(db.Integer, primary_key=True)  
    # Primary key for each product

    name = db.Column(db.String(100), nullable=False)  
    # Name of the product, cannot be empty

    description = db.Column(db.Text, nullable=False)  
    # Detailed product description

    price = db.Column(db.Float, nullable=False)  
    # Product price (stored as float for decimal values)

    image = db.Column(db.String(100), nullable=False)  
    # Image filename or URL for the product

    category = db.Column(db.String(50), nullable=False)
    # Product category for filtering and grouping products

    reviews = db.relationship('Review', back_populates='product', lazy=True)  
    # One-to-many relationship: a product can have multiple reviews

    # Helper method to convert product data into dictionary format (useful for APIs)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image,
            "category": self.category
        }

# ============================== CART MODEL ==============================
# Represents the shopping cart where users add products before purchasing
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    # Primary key for each cart item

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    # Foreign key linking cart item to the user who owns it
    # 'user.id' points to the 'id' column in the User model

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  
    # Foreign key linking cart item to the product

    product_name = db.Column(db.String(100), nullable=False)  
    # Name of the product (stored for quick access without extra joins)

    product_image = db.Column(db.String(200), nullable=False)  
    # Image of the product in the cart

    product_description = db.Column(db.Text, nullable=False)  
    # Description of the product

    quantity = db.Column(db.Integer, default=1, nullable=False)  
    # Quantity of this product in the cart, default is 1

    added_at = db.Column(db.DateTime, default=datetime.utcnow)  
    # Timestamp when the product was added to the cart

    product_price = db.Column(db.Float, nullable=False)  
    # Price of the product at the time it was added to the cart

# ============================== ORDER MODEL ==============================
# Represents finalized orders after a user completes the checkout process
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Primary key for each order

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Foreign key linking the order to the user who placed it

    product_name = db.Column(db.String(100), nullable=False)
    # Name of the purchased product

    product_image = db.Column(db.String(200), nullable=False)
    # Image of the product

    product_description = db.Column(db.Text, nullable=False)
    # Description of the product

    product_price = db.Column(db.Float, nullable=False)
    # Price of the product at purchase time

    quantity = db.Column(db.Integer, nullable=False)
    # Quantity of this product ordered

    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Timestamp when the order was placed

# ============================== REVIEW MODEL ==============================
# Represents reviews that users leave on products
class Review(db.Model):
    __tablename__ = 'review'  # Explicitly naming the table

    id = db.Column(db.Integer, primary_key=True)
    # Primary key for each review

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Foreign key linking review to the user who wrote it

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    # Foreign key linking review to the product being reviewed

    content = db.Column(db.Text, nullable=False)
    # The actual review text

    rating = db.Column(db.Integer, nullable=False)
    # Numerical rating (e.g., 1-5 stars)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Timestamp when the review was created

    # Relationship back to User (a review is written by a user)
    user = db.relationship('User', back_populates='reviews')

    # Relationship back to Product (a review belongs to a product)
    product = db.relationship('Product', back_populates='reviews')

    # Helper method to return review data as dictionary (e.g., for API responses)
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "content": self.content,
            "user_name": self.user.username if self.user else None,  # Safely get username
            "product_name": self.product.name if self.product else None,  # Safely get product name
            "rating": self.rating,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

# ============================== ADMIN MODEL ==============================
# Represents separate admin users who have full access to manage the system
class Admin(UserMixin, db.Model):
    __tablename__ = "admin_user"  # Table for admin users

    id = db.Column(db.Integer, primary_key=True)
    # Primary key for each admin

    username = db.Column(db.String(100), unique=True, nullable=False)
    # Unique username for admin login

    password = db.Column(db.String(200), nullable=False)
    # Hashed password for security

    @property
    def is_admin(self):
        # Always return True to indicate this user is an admin
        return True
