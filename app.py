# from flask import Flask, request, jsonify, redirect, url_for, render_template, flash, abort, current_app
# from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# from flask_pymongo import PyMongo
# from dotenv import load_dotenv
# from waitress import serve
# import os
# import logging
# from forms import LoginForm, RegisterForm
# import razorpay
# import time
# from razorpay.errors import SignatureVerificationError
# from functools import wraps
# from bson.objectid import ObjectId

# # Load environment variables
# load_dotenv()

# # ================================= APP CONFIG =================================
# app = Flask(__name__)
# app.secret_key = os.getenv("SECRET_KEY")

# # Load MongoDB URI from environment
# app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# # Initialize MongoDB
# mongo = PyMongo(app)

# # Replace with your Razorpay Test Keys
# RAZORPAY_KEY_ID = "rzp_test_RGwtqT5wceiJFe"
# RAZORPAY_KEY_SECRET = "YeZN5pc6WvaL0Ag9uC3XoAFK"
# razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# # ================================= LOGIN CONFIG ===============================
# login_manager = LoginManager()
# login_manager.login_view = "login"
# login_manager.init_app(app)


# # Helper class for Flask-Login
# class AdminUser(UserMixin):
#     def __init__(self, user_id, username, is_admin=True):
#         self.id = str(user_id)
#         self.username = username
#         self.is_admin = is_admin


# @login_manager.user_loader
# def load_user(user_id):
#     # First, check in Admin collection
#     admin = mongo.db.Admin.find_one({"_id": user_id})
#     if admin:
#         return AdminUser(user_id=admin["_id"], username=admin["username"], is_admin=True)

#     # If not admin, check in User collection
#     user = mongo.db.User.find_one({"_id": user_id})
#     if user:
#         return AdminUser(user_id=user["_id"], username=user["username"], is_admin=False)

#     return None



# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # Check if user is logged in
#         if not current_user.is_authenticated:
#             flash("You must be logged in to access this page.", "warning")
#             return redirect(url_for("login"))  # Change to your normal login route

#         # Check if the logged-in user is an admin
#         if not getattr(current_user, "is_admin", False):
#             flash("Admin access required.", "danger")
#             return redirect(url_for("home"))  # Redirect to a safe page

#         return f(*args, **kwargs)
#     return decorated_function

# # ================================= ROUTES =====================================

# @app.route('/')
# def home():
#     """Public home page displaying all products."""
#     products = list(mongo.db.products.find())
#     # Convert ObjectId to string for templates
#     for p in products:
#         p["_id"] = str(p["_id"])
#     return render_template('index.html', products=products, current_page='home')


# # ---------- Admin Authentication ----------
# @app.route("/admin_login", methods=["GET", "POST"])
# def admin_login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         user = mongo.db.Admin.find_one({"username": username})
#         if user and check_password_hash(user["password"], password):
#             login_user(AdminUser(user_id=user["_id"], username=user["username"], is_admin=True))
#             return redirect(url_for("dashboard"))

#         flash("Invalid credentials", "danger")
#     return render_template("admin_login.html")


# @app.route("/admin_logout")
# @admin_required
# def admin_logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("admin_login"))


# @app.route("/dashboard")
# @admin_required
# def dashboard():
#     return render_template("admin_dashboard.html")


# # ---------- Admin View Pages ----------
# @app.route("/products")
# @admin_required
# def view_products():
#     products = list(mongo.db.products.find())
#     for p in products:
#         p["_id"] = str(p["_id"])
#     return render_template("admin_view_product.html", products=products)


# @app.route("/reviews")
# @admin_required
# def view_reviews():
#     reviews = list(mongo.db.reviews.find())
#     for r in reviews:
#         r["_id"] = str(r["_id"])
#     return render_template("admin_review.html", reviews=reviews)


# # ========================== Product Management API ==========================

# # Add Product
# @app.route('/ecommerce/add', methods=['POST'])
# @admin_required
# def add_product():
#     data = request.form
#     image_file = request.files.get('image')

#     if not all([data.get('name'), data.get('description'),
#                 data.get('category'), data.get('price'), image_file]):
#         return jsonify({"error": "All fields are required"}), 400

#     try:
#         price = float(data.get('price'))
#         if price <= 0:
#             return jsonify({"error": "Price must be greater than zero"}), 400
#     except (TypeError, ValueError):
#         return jsonify({"error": "Invalid price format"}), 400

#     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#     def allowed_file(filename):
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#     filename = secure_filename(image_file.filename)
#     if not allowed_file(filename):
#         return jsonify({"error": "Invalid image format. Allowed: png, jpg, jpeg, gif"}), 400

#     image_path = os.path.join(app.static_folder, "images", filename)
#     image_file.save(image_path)

#     product_data = {
#         "name": data['name'],
#         "description": data['description'],
#         "category": data['category'],
#         "price": price,
#         "image": filename
#     }
#     result = mongo.db.products.insert_one(product_data)
#     product_data["_id"] = str(result.inserted_id)

#     return jsonify(product_data), 201


# # Fetch All Products
# @app.route("/ecommerce/products")
# @admin_required
# def get_products():
#     products = list(mongo.db.products.find())
#     for p in products:
#         p["_id"] = str(p["_id"])
#     return jsonify(products)


# # Update Product
# @app.route("/ecommerce/update/<product_id>", methods=["POST", "PUT"])
# @admin_required
# def update_product(product_id):
#     from bson.errors import InvalidId
#     try:
#         product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
#         if not product:
#             return jsonify({"error": "Product not found"}), 404
#     except InvalidId:
#         return jsonify({"error": "Invalid product ID"}), 400

#     update_data = {}
#     for field in ["name", "description", "category"]:
#         value = request.form.get(field)
#         if value:
#             update_data[field] = value.strip()

#     price_input = request.form.get("price")
#     if price_input:
#         try:
#             price = float(price_input)
#             if price <= 0:
#                 return jsonify({"error": "Price must be greater than zero"}), 400
#             update_data["price"] = price
#         except ValueError:
#             return jsonify({"error": "Invalid price format"}), 400

#     image_file = request.files.get("image")
#     if image_file and image_file.filename:
#         filename = secure_filename(image_file.filename)
#         ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#         if not filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
#             return jsonify({"error": "Invalid image format"}), 400

#         image_path = os.path.join(app.static_folder, "images", filename)
#         image_file.save(image_path)
#         update_data["image"] = filename

#     mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
#     updated_product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
#     updated_product["_id"] = str(updated_product["_id"])
#     return jsonify(updated_product), 200


# # Delete Product
# @app.route("/ecommerce/delete/<product_id>", methods=["DELETE"])
# @admin_required
# def delete_product(product_id):
#     from bson.errors import InvalidId
#     try:
#         result = mongo.db.products.delete_one({"_id": ObjectId(product_id)})
#     except InvalidId:
#         return jsonify({"error": "Invalid product ID"}), 400

#     if result.deleted_count == 0:
#         return jsonify({"error": "Failed to delete product"}), 500
#     return jsonify({"message": "Product deleted successfully"})


# # ========================== Review Management API ==========================
# @app.route("/ecommerce/reviews")
# @admin_required
# def get_reviews():
#     reviews = list(mongo.db.reviews.find())
#     for r in reviews:
#         r["_id"] = str(r["_id"])
#     return jsonify(reviews)


# @app.route("/ecommerce/reviews/<review_id>/delete", methods=["POST"])
# @admin_required
# def delete_review(review_id):
#     from bson.errors import InvalidId
#     try:
#         result = mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
#     except InvalidId:
#         flash("Invalid review ID", "danger")
#         return redirect(url_for('view_reviews'))

#     if result.deleted_count == 0:
#         flash("Failed to delete review. Please try again.", "danger")
#     else:
#         flash("Review deleted successfully!", "success")

#     return redirect(url_for('view_reviews'))

# # ==========================
# # 1. Create a New Order (Razorpay)
# # ==========================
# @app.route('/create_order', methods=['POST'])
# def create_order():
#     try:
#         data = request.get_json()
#         try:
#             amount = int(float(data.get("amount")) * 100)
#         except (ValueError, TypeError):
#             return jsonify({"error": "Invalid amount format"}), 400

#         if amount <= 0:
#             return jsonify({"error": "Invalid amount"}), 400

#         order = razorpay_client.order.create({
#             'amount': amount,
#             'currency': 'INR',
#             'payment_capture': '1',
#             'receipt': f"order_rcpt_{int(time.time())}"
#         })

#         return jsonify(order), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # ==========================
# # 2. Verify Payment
# # ==========================
# @app.route("/verify", methods=["POST"])
# @login_required
# def verify_payment():
#     data = request.get_json()
#     try:
#         razorpay_client.utility.verify_payment_signature({
#             "razorpay_order_id": data["razorpay_order_id"],
#             "razorpay_payment_id": data["razorpay_payment_id"],
#             "razorpay_signature": data["razorpay_signature"]
#         })

#         # MongoDB: Loop through cart items and create order records
#         cart_items = list(mongo.db.cart.find({"user_id": current_user._id}))

#         for item in cart_items:
#             mongo.db.orders.insert_one({
#                 "user_id": current_user._id,
#                 "product_name": item['product_name'],
#                 "product_image": item['product_image'],
#                 "product_description": item['product_description'],
#                 "product_price": item['product_price'],
#                 "quantity": item['quantity'],
#                 "ordered_at": time.time()
#             })

#         # Clear cart
#         mongo.db.cart.delete_many({"user_id": current_user._id})

#         return jsonify({"status": "success", "redirect_url": url_for('orders')})

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"status": "failure", "error": str(e)}), 400


# # ====================================================== User Section =========================================================
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         username = form.username.data.strip()
#         email = form.email.data.strip()

#         existing_user = mongo.db.users.find_one({
#             "$or": [{"email": email}, {"username": username}]
#         })

#         if existing_user:
#             flash('Email or username already exists. Please choose another.', 'warning')
#             return render_template('register.html', form=form)

#         hashed_pw = generate_password_hash(form.password.data)
#         user_data = {
#             "username": username,
#             "email": email,
#             "password": hashed_pw,
#             "is_admin": False
#         }
#         result = mongo.db.users.insert_one(user_data)
#         flash('Account created successfully!', 'success')
#         return redirect(url_for('login'))

#     return render_template('register.html', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         email = form.email.data.strip()
#         password = form.password.data

#         user_data = mongo.db.users.find_one({"email": email})
#         if user_data and check_password_hash(user_data['password'], password):
#             user = UserObject(user_data)  # Wrap Mongo document into UserObject compatible with Flask-Login
#             login_user(user)
#             flash('Logged in successfully!', 'success')
#             app.logger.info(f"User {user.username} logged in.")
#             return redirect(url_for('home'))
#         else:
#             flash('Invalid email or password. Please try again.', 'danger')
#             app.logger.warning(f"Failed login attempt for email: {email}")

#     return render_template('login.html', form=form)


# @app.route('/logout')
# @login_required
# def logout():
#     username = current_user.username
#     logout_user()
#     flash('You have been logged out.', 'success')
#     app.logger.info(f"User '{username}' logged out.")
#     return redirect(url_for('login'))


# @app.route('/product/<product_id>')
# def product_detail(product_id):
#     product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
#     if not product:
#         abort(404)
#     return render_template('product_details.html', product=product)


# @app.route('/add-to-cart/<product_id>')
# @login_required
# def add_to_cart(product_id):
#     product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
#     if not product:
#         abort(404)

#     existing_item = mongo.db.cart.find_one({"user_id": current_user._id, "product_id": product_id})

#     if existing_item:
#         mongo.db.cart.update_one({"_id": existing_item["_id"]}, {"$inc": {"quantity": 1}})
#     else:
#         mongo.db.cart.insert_one({
#             "user_id": current_user._id,
#             "product_id": product_id,
#             "product_name": product['name'],
#             "product_image": product['image'],
#             "product_description": product['description'],
#             "product_price": product['price'],
#             "quantity": 1
#         })

#     flash(f"{product['name']} added to cart!", "success")
#     return redirect(url_for('home'))


# @app.route('/cart')
# @login_required
# def cart():
#     cart_items = list(mongo.db.cart.find({"user_id": current_user._id}))
#     total_price = sum(item['quantity'] * item['product_price'] for item in cart_items)
#     RAZORPAY_KEY_ID = "rzp_test_RGwtqT5wceiJFe"

#     return render_template(
#         'cart.html',
#         cart_items=cart_items,
#         total_price=total_price,
#         RAZORPAY_KEY_ID=RAZORPAY_KEY_ID,
#         current_page='cart'
#     )


# @app.route('/update-cart/<cart_id>', methods=['POST'])
# @login_required
# def update_cart(cart_id):
#     quantity = int(request.form['quantity'])
#     item = mongo.db.cart.find_one({"_id": ObjectId(cart_id)})
#     if not item or item['user_id'] != current_user._id:
#         abort(403)
#     mongo.db.cart.update_one({"_id": ObjectId(cart_id)}, {"$set": {"quantity": quantity}})
#     flash("Cart updated!", "success")
#     return redirect(url_for('cart'))


# @app.route('/remove-from-cart/<cart_id>')
# @login_required
# def remove_from_cart(cart_id):
#     item = mongo.db.cart.find_one({"_id": ObjectId(cart_id)})
#     if not item or item['user_id'] != current_user._id:
#         abort(403)
#     mongo.db.cart.delete_one({"_id": ObjectId(cart_id)})
#     flash("Item removed from cart.", "info")
#     return redirect(url_for('cart'))


# @app.route('/checkout')
# @login_required
# def checkout():
#     cart_items = list(mongo.db.cart.find({"user_id": current_user._id}))
#     if not cart_items:
#         flash("Your cart is empty. Add items before checking out.", "warning")
#         return redirect(url_for('cart'))

#     try:
#         for item in cart_items:
#             mongo.db.orders.insert_one({
#                 "user_id": current_user._id,
#                 "product_name": item['product_name'],
#                 "product_image": item['product_image'],
#                 "product_description": item['product_description'],
#                 "product_price": item['product_price'],
#                 "quantity": item['quantity'],
#                 "ordered_at": time.time()
#             })
#             mongo.db.cart.delete_one({"_id": item["_id"]})

#         flash("Your order has been placed!", "success")
#         app.logger.info(f"User {current_user.username} placed an order with {len(cart_items)} items.")
#         return redirect(url_for('orders'))

#     except Exception as e:
#         app.logger.error(f"Checkout failed for user {current_user.username}: {str(e)}")
#         flash("Something went wrong during checkout. Please try again.", "danger")
#         return redirect(url_for('cart'))


# @app.route('/orders')
# @login_required
# def orders():
#     user_orders = list(mongo.db.orders.find({"user_id": current_user._id}).sort("ordered_at", -1))
#     return render_template('orders.html', orders=user_orders, current_page='order')


# @app.route('/add-review/<product_id>', methods=['POST'])
# @login_required
# def add_review(product_id):
#     content = request.form.get('content')
#     rating = int(request.form.get('rating'))
#     mongo.db.reviews.insert_one({
#         "user_id": current_user._id,
#         "product_id": product_id,
#         "content": content,
#         "rating": rating,
#         "created_at": time.time()
#     })
#     flash("Review submitted!", "success")
#     return redirect(url_for('product_detail', product_id=product_id))





# # ================================= RUN APP ====================================
# if __name__ == "__main__":
#     print("Starting Witress on http://localhost:5000")
#     serve(app, host="0.0.0.0", port=5000)


























from flask import Flask, request, jsonify, redirect, url_for, render_template, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from waitress import serve
import os, logging, time
from functools import wraps
from bson.objectid import ObjectId
from forms import LoginForm, RegisterForm
import razorpay

# ------------------ Load Environment Variables ------------------
load_dotenv()

# ------------------ Flask App & Config ------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# ------------------ Razorpay Client ------------------
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID") or "rzp_test_RGwtqT5wceiJFe"
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET") or "YeZN5pc6WvaL0Ag9uC3XoAFK"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ------------------ Flask-Login ------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ------------------ User Class for Flask-Login ------------------
class UserObject(UserMixin):
    def __init__(self, user_doc, is_admin=False):
        self.id = str(user_doc["_id"])
        self.username = user_doc.get("username")
        self.is_admin = is_admin
        self._doc = user_doc
# Make sure this is above the admin_login route
class AdminUser(UserMixin):
    def __init__(self, user_id, username, is_admin=True):
        self.id = str(user_id)
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    # Check Admins first
    admin_doc = mongo.db.Admin.find_one({"_id": ObjectId(user_id)})
    if admin_doc:
        return UserObject(admin_doc, is_admin=True)
    # Check normal users
    user_doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return UserObject(user_doc)
    return None

# ------------------ Admin Required Decorator ------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Login required", "warning")
            return redirect(url_for("login"))
        if not getattr(current_user, "is_admin", False):
            flash("Admin access only", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

# ------------------ Routes ------------------

@app.route('/')
def home():
    products = list(mongo.db.products.find())
    for p in products:
        p["_id"] = str(p["_id"])
    return render_template('index.html', products=products, current_page='home')

# ------------------ Admin Routes ------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch admin from MongoDB
        admin_doc = mongo.db.Admin.find_one({"username": username})

        # Simple plain-text password check
        if admin_doc and admin_doc.get("password") == password:
            login_user(AdminUser(user_id=admin_doc["_id"], username=admin_doc["username"], is_admin=True))
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")
    return render_template("admin_login.html")


@app.route("/admin_logout")
@admin_required
def admin_logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("admin_login"))

@app.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin_dashboard.html")

@app.route("/products")
@admin_required
def view_products():
    try:
        # Fetch all products from MongoDB
        products = list(mongo.db.products.find())
        
        # Convert ObjectId to string and ensure all fields exist
        for p in products:
            p["_id"] = str(p.get("_id", ""))
            p["name"] = p.get("name", "No Name")
            p["description"] = p.get("description", "No Description")
            p["category"] = p.get("category", "Uncategorized")
            p["price"] = float(p.get("price", 0.0))
            p["image"] = p.get("image", "default.png")  # Provide default image if missing
        
        return render_template("admin_view_product.html", products=products)
    
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        flash("Failed to load products. Please try again later.", "danger")
        return render_template("admin_view_product.html", products=[])


@app.route("/reviews")
@admin_required
def view_reviews():
    reviews = list(mongo.db.reviews.find())
    for r in reviews:
        r["_id"] = str(r["_id"])
    return render_template("admin_review.html", reviews=reviews)

# ------------------ Product API ------------------
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ecommerce/add', methods=['POST'])
@admin_required
def add_product():
    data = request.form
    image_file = request.files.get('image')
    if not all([data.get('name'), data.get('description'), data.get('category'), data.get('price'), image_file]):
        return jsonify({"error":"All fields required"}),400
    try:
        price = float(data.get("price"))
        if price<=0: return jsonify({"error":"Price must >0"}),400
    except: return jsonify({"error":"Invalid price"}),400
    filename = secure_filename(image_file.filename)
    if not allowed_file(filename):
        return jsonify({"error":"Invalid image format"}),400
    image_file.save(os.path.join(app.static_folder,"images",filename))
    product_data = {
        "name":data["name"], "description":data["description"], "category":data["category"],
        "price":price, "image":filename
    }
    result = mongo.db.products.insert_one(product_data)
    product_data["_id"] = str(result.inserted_id)
    return jsonify(product_data),201

@app.route("/ecommerce/update/<product_id>", methods=["POST","PUT"])
@admin_required
def update_product(product_id):
    try:
        prod = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if not prod: return jsonify({"error":"Not found"}),404
    except: return jsonify({"error":"Invalid ID"}),400
    update_data = {}
    for f in ["name","description","category"]:
        v=request.form.get(f)
        if v: update_data[f]=v.strip()
    price_input = request.form.get("price")
    if price_input:
        try:
            price=float(price_input)
            if price<=0: return jsonify({"error":"Price must >0"}),400
            update_data["price"]=price
        except: return jsonify({"error":"Invalid price"}),400
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        filename=secure_filename(image_file.filename)
        if not allowed_file(filename): return jsonify({"error":"Invalid image format"}),400
        image_file.save(os.path.join(app.static_folder,"images",filename))
        update_data["image"]=filename
    mongo.db.products.update_one({"_id":ObjectId(product_id)},{"$set":update_data})
    updated = mongo.db.products.find_one({"_id":ObjectId(product_id)})
    updated["_id"]=str(updated["_id"])
    return jsonify(updated),200

@app.route("/ecommerce/delete/<product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    try:
        result = mongo.db.products.delete_one({"_id":ObjectId(product_id)})
        if result.deleted_count==0: return jsonify({"error":"Delete failed"}),500
        return jsonify({"message":"Deleted"}),200
    except: return jsonify({"error":"Invalid ID"}),400

# ------------------ Review API ------------------
@app.route("/ecommerce/reviews/<review_id>/delete", methods=["POST"])
@admin_required
def delete_review(review_id):
    try:
        result=mongo.db.reviews.delete_one({"_id":ObjectId(review_id)})
        flash("Deleted" if result.deleted_count else "Failed delete","success" if result.deleted_count else "danger")
    except: flash("Invalid ID","danger")
    return redirect(url_for('view_reviews'))

# ------------------ User Auth ------------------
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username,email=form.username.data.strip(),form.email.data.strip()
        if mongo.db.users.find_one({"$or":[{"username":username},{"email":email}]}):
            flash("Email/Username exists","warning")
            return render_template("register.html",form=form)
        hashed=generate_password_hash(form.password.data)
        mongo.db.users.insert_one({"username":username,"email":email,"password":hashed,"is_admin":False})
        flash("Account created","success")
        return redirect(url_for("login"))
    return render_template("register.html",form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data.strip()
        pw=form.password.data
        user_doc=mongo.db.users.find_one({"email":email})
        if user_doc and check_password_hash(user_doc["password"],pw):
            login_user(UserObject(user_doc))
            flash("Logged in","success")
            return redirect(url_for("home"))
        flash("Invalid email/password","danger")
    return render_template("login.html",form=form)

@app.route('/logout')
@login_required
def logout():
    uname=current_user.username
    logout_user()
    flash("Logged out","success")
    return redirect(url_for("login"))

# ------------------ Product & Cart ------------------
@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product=mongo.db.products.find_one({"_id":ObjectId(product_id)})
        if not product: abort(404)
        return render_template("product_details.html", product=product)
    except: abort(404)

@app.route('/add_to_cart/<product_id>')
@login_required
def add_to_cart(product_id):
    try:
        product=mongo.db.products.find_one({"_id":ObjectId(product_id)})
        if not product: abort(404)
        existing=mongo.db.cart.find_one({"user_id":ObjectId(current_user.id),"product_id":product_id})
        if existing:
            mongo.db.cart.update_one({"_id":existing["_id"]},{"$inc":{"quantity":1}})
        else:
            mongo.db.cart.insert_one({
                "user_id":ObjectId(current_user.id),
                "product_id":product_id,
                "product_name":product["name"],
                "product_image":product["image"],
                "product_description":product["description"],
                "product_price":product["price"],
                "quantity":1
            })
        flash(f"{product['name']} added","success")
        return redirect(url_for('home'))
    except: abort(500)

@app.route('/cart')
@login_required
def cart():
    items=list(mongo.db.cart.find({"user_id":ObjectId(current_user.id)}))
    total=sum(i["quantity"]*i["product_price"] for i in items)
    return render_template("cart.html", cart_items=items, total_price=total, RAZORPAY_KEY_ID=RAZORPAY_KEY_ID, current_page='cart')

@app.route('/update_cart/<cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    qty=int(request.form["quantity"])
    mongo.db.cart.update_one({"_id":ObjectId(cart_id),"user_id":ObjectId(current_user.id)},{"$set":{"quantity":qty}})
    flash("Cart updated","success")
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<cart_id>')
@login_required
def remove_from_cart(cart_id):
    mongo.db.cart.delete_one({"_id":ObjectId(cart_id),"user_id":ObjectId(current_user.id)})
    flash("Removed from cart","info")
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    items=list(mongo.db.cart.find({"user_id":ObjectId(current_user.id)}))
    if not items: flash("Cart empty","warning"); return redirect(url_for('cart'))
    for item in items:
        mongo.db.orders.insert_one({
            "user_id":ObjectId(current_user.id),
            "product_name":item["product_name"],
            "product_image":item["product_image"],
            "product_description":item["product_description"],
            "product_price":item["product_price"],
            "quantity":item["quantity"],
            "ordered_at":time.time()
        })
        mongo.db.cart.delete_one({"_id":item["_id"]})
    flash("Order placed","success")
    return redirect(url_for('orders'))

@app.route('/orders')
@login_required
def orders():
    user_orders=list(mongo.db.orders.find({"user_id":ObjectId(current_user.id)}).sort("ordered_at",-1))
    return render_template("orders.html", orders=user_orders, current_page='order')

@app.route('/add-review/<product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    content=request.form.get("content")
    rating=int(request.form.get("rating"))
    mongo.db.reviews.insert_one({
        "user_id":ObjectId(current_user.id),
        "product_id":product_id,
        "content":content,
        "rating":rating,
        "created_at":time.time()
    })
    flash("Review submitted","success")
    return redirect(url_for('product_detail', product_id=product_id))

# ------------------ Razorpay Integration ------------------
@app.route('/create_order', methods=['POST'])
def create_order():
    data=request.get_json()
    try:
        amount=int(float(data.get("amount"))*100)
        if amount<=0: return jsonify({"error":"Invalid amount"}),400
        order=razorpay_client.order.create({
            "amount":amount,"currency":"INR","payment_capture":"1","receipt":f"order_rcpt_{int(time.time())}"
        })
        return jsonify(order),200
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/verify", methods=["POST"])
@login_required
def verify_payment():
    data=request.get_json()
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id":data["razorpay_order_id"],
            "razorpay_payment_id":data["razorpay_payment_id"],
            "razorpay_signature":data["razorpay_signature"]
        })
        cart_items=list(mongo.db.cart.find({"user_id":ObjectId(current_user.id)}))
        for item in cart_items:
            mongo.db.orders.insert_one({
                "user_id":ObjectId(current_user.id),
                "product_name":item['product_name'],
                "product_image":item['product_image'],
                "product_description":item['product_description'],
                "product_price":item['product_price'],
                "quantity":item['quantity'],
                "ordered_at":time.time()
            })
        mongo.db.cart.delete_many({"user_id":ObjectId(current_user.id)})
        return jsonify({"status":"success","redirect_url":url_for('orders')})
    except Exception as e:
        return jsonify({"status":"failure","error":str(e)}),400

# ------------------ Run App ------------------
if __name__=="__main__":
    print("Starting Waitress on http://localhost:5000")
    serve(app, host="0.0.0.0", port=5000)
