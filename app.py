from flask import Flask, request, jsonify, redirect, url_for, render_template, flash, abort
from models import db, Product, User, Review, Admin, Cart, Order
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import razorpay
import time
from razorpay.errors import SignatureVerificationError
from forms import RegisterForm, LoginForm
from functools import wraps
from flask import current_app
from waitress import serve
# ================================= APP CONFIG =================================
app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Replace with your Razorpay Test Keys
RAZORPAY_KEY_ID = "rzp_test_RGwtqT5wceiJFe"
RAZORPAY_KEY_SECRET = "YeZN5pc6WvaL0Ag9uC3XoAFK"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
# ================================= LOGIN CONFIG ===============================
login_manager = LoginManager()
login_manager.login_view = "login"  
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    admin = db.session.get(Admin, int(user_id))
    if admin:
        return admin
    return db.session.get(User, int(user_id))


# Create tables + default admin
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username="admin").first():
        admin = Admin(username="admin", password=generate_password_hash("admin123"))
        db.session.add(admin)
        db.session.commit()




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# ================================= ROUTES =====================================

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products, current_page='home')

# ---------- AUTH ----------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = Admin.query.filter_by(username=request.form.get("username")).first()
        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("admin_login.html")

@app.route("/admin_logout")
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))


@app.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin_dashboard.html")

# ---------- VIEWS ----------
@app.route("/products")
@admin_required
def product():
    return render_template("admin_view_product.html", products=Product.query.all())

@app.route("/reviews")
@admin_required
def review():
    return render_template("admin_review.html", reviews=Review.query.all())

# ---------- PRODUCT API ----------
@app.route('/ecommerce/add', methods=['POST'])
@admin_required
def add_product():
    data = request.form
    image_file = request.files.get('image')

    # Validate required fields
    if not all([data.get('name'), data.get('description'), data.get('category'), data.get('price'), image_file]):
        return jsonify({"error": "All fields are required"}), 400

    # Validate price format and value
    try:
        price = float(data.get('price'))
        if price <= 0:
            return jsonify({"error": "Price must be greater than zero"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid price format"}), 400

    # Validate image format
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    filename = secure_filename(image_file.filename)
    if not allowed_file(filename):
        return jsonify({"error": "Invalid image format. Allowed formats: png, jpg, jpeg, gif"}), 400

    # Save image
    image_path = os.path.join(app.static_folder, "images", filename)
    image_file.save(image_path)

    # Create and save product
    new_product = Product(
        name=data['name'],
        description=data['description'],
        category=data['category'],
        price=price,
        image=filename
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify(new_product.to_dict())

@app.route("/ecommerce/products")
@admin_required
def get_products():
    return jsonify([p.to_dict() for p in Product.query.all()])

@app.route("/ecommerce/update/<int:product_id>", methods=["POST", "PUT"])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Validate and update name
    name = request.form.get("name")
    if name:
        product.name = name.strip()

    # Validate and update description
    description = request.form.get("description")
    if description:
        product.description = description.strip()

    # Validate and update category
    category = request.form.get("category")
    if category:
        product.category = category.strip()

    # Validate and update price
    price_input = request.form.get("price")
    if price_input:
        try:
            price = float(price_input)
            if price <= 0:
                return jsonify({"error": "Price must be greater than zero"}), 400
            product.price = price
        except ValueError:
            return jsonify({"error": "Invalid price format"}), 400

    # Validate and update image
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)

        # Check allowed extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if not allowed_file(filename):
            return jsonify({"error": "Invalid image format"}), 400

        image_path = os.path.join(app.static_folder, "images", filename)
        image_file.save(image_path)
        product.image = filename

    # Commit changes
    db.session.commit()
    return jsonify(product.to_dict())


@app.route("/ecommerce/delete/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product '{product.name}' deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete product"}), 500

# ---------- REVIEW API ----------
@app.route("/ecommerce/reviews")
@admin_required
def get_reviews():
    return jsonify([review.to_dict() for review in Review.query.all()])

@app.route("/ecommerce/reviews/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Optional: Log the deletion action
    app.logger.info(f"Admin {current_user.username} deleted review ID {review_id}")

    try:
        db.session.delete(review)
        db.session.commit()
        flash("Review deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting review ID {review_id}: {str(e)}")
        flash("Failed to delete review. Please try again.", "danger")

    return redirect(url_for('review'))

# ==========================
# 1. Create a New Order
# ==========================
@app.route('/create_order', methods=['POST'])
def create_order():
    """
    This endpoint creates a Razorpay order.
    The frontend sends an amount in INR, and we convert it to paise before creating the order.
    """
    try:
        data = request.get_json()
        try:
            amount = int(float(data.get("amount")) * 100)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount format"}), 400

        # Validate amount
        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Create order on Razorpay
        order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1',  # Auto-capture payment
            'receipt': f"order_rcpt_{int(time.time())}"  # Unique receipt ID
        })

        return jsonify(order), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 2. Verify Payment
# ==========================
@app.route("/verify", methods=["POST"])
@login_required
def verify_payment():
    data = request.get_json()
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        # Loop through cart items and create individual Order records
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            new_order = Order(
                user_id=current_user.id,
                product_name=item.product_name,
                product_image=item.product_image,
                product_description=item.product_description,
                product_price=item.product_price,
                quantity=item.quantity
            )
            db.session.add(new_order)

        # Clear the cart
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        return jsonify({"status": "success", "redirect_url": url_for('orders')})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "failure", "error": str(e)}), 400




# ====================================================== User Section =========================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Strip whitespace from inputs
        username = form.username.data.strip()
        email = form.email.data.strip()

        # Check for existing user by email or username
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            flash('Email or username already exists. Please choose another.', 'warning')
            return render_template('register.html', form=form)

        # Hash password and create user
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            username=username,
            email=email,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Strip whitespace from email input
        email = form.email.data.strip()
        password = form.password.data

        # Query user by email
        user = User.query.filter_by(email=email).first()

        # Validate credentials
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            app.logger.info(f"User {user.username} logged in.")
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            app.logger.warning(f"Failed login attempt for email: {email}")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    username = current_user.username  # Capture username before logout
    logout_user()
    flash('You have been logged out.', 'success')

    # Optional: Log the logout action
    app.logger.info(f"User '{username}' logged out.")

    return redirect(url_for('login'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)

@app.route('/add-to-cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(
        user_id=current_user.id,
        product_id=product.id,
        product_name=product.name,
        product_image=product.image,
        product_description=product.description,
        product_price=product.price,
        quantity=1
)

        db.session.add(new_item)

    db.session.commit()
    flash(f"{product.name} added to cart!", "success")
    return redirect(url_for('home'))

#cart
@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    # total_price = sum(item.quantity * Product.query.get(item.product_id).price for item in cart_items)
    total_price = sum(item.quantity * db.session.get(Product, item.product_id).price for item in cart_items)
    RAZORPAY_KEY_ID = "rzp_test_RGwtqT5wceiJFe"  # Replace with your actual test/live key

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total_price=total_price,
        RAZORPAY_KEY_ID=RAZORPAY_KEY_ID,
        current_page='cart'  # 👈 This enables context-aware search
    )

@app.route('/search')
@login_required
def search():
    query = request.args.get('query')
    page = request.args.get('page')

    valid_pages = ['home', 'cart', 'order']
    if page not in valid_pages:
        page = 'home'

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for(page))

    results = []

    if page == 'home':
        results = Product.query.filter(Product.name.ilike(f"%{query}%")).all()

    elif page == 'cart':
        raw_results = Cart.query.filter_by(user_id=current_user.id).filter(
            Cart.product_name.ilike(f"%{query}%")
        ).all()
        results = [{
            'id': item.product_id,
            'name': item.product_name,
            'description': item.product_description,
            'image': item.product_image,
            'price': item.product_price,
            'quantity': item.quantity
        } for item in raw_results]

    elif page == 'order':
        raw_results = Order.query.filter_by(user_id=current_user.id).filter(
            Order.product_name.ilike(f"%{query}%")
    ).all()
        results = [{
            'id': None,  # No product_id available, so skip linking
            'name': item.product_name,
            'description': item.product_description,
            'image': item.product_image,
            'price': item.product_price,
            'quantity': item.quantity,
            'ordered_at': item.ordered_at
    } for item in raw_results]


    logging.info(f"Search query: '{query}' | Page: '{page}' | Results found: {len(results)}")

    return render_template(
        'search_results.html',
        results=results,
        query=query,
        current_page=page
    )



#suupporting routes
@app.route('/update-cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id != current_user.id:
        abort(403)
    item.quantity = int(request.form['quantity'])
    db.session.commit()
    flash("Cart updated!", "success")
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    item = Cart.query.get_or_404(cart_id)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash("Your cart is empty. Add items before checking out.", "warning")
        return redirect(url_for('cart'))

    try:
        for item in cart_items:
            order = Order(
                user_id=item.user_id,
                product_name=item.product_name.strip(),
                product_image=item.product_image,
                product_description=item.product_description.strip(),
                product_price=item.product_price,
                quantity=item.quantity
            )
            db.session.add(order)
            db.session.delete(item)  # Clear cart

        db.session.commit()
        flash("Your order has been placed!", "success")
        app.logger.info(f"User {current_user.username} placed an order with {len(cart_items)} items.")
        return redirect(url_for('orders'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Checkout failed for user {current_user.username}: {str(e)}")
        flash("Something went wrong during checkout. Please try again.", "danger")
        return redirect(url_for('cart'))


@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.ordered_at.desc()).all()
    return render_template(
        'orders.html',
        orders=user_orders,
        current_page='order'  # 👈 Enables context-aware search
    )
#review
@app.route('/add-review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    content = request.form.get('content')
    rating = int(request.form.get('rating'))
    review = Review(user_id=current_user.id, product_id=product_id, content=content, rating=rating)
    db.session.add(review)
    db.session.commit()
    flash("Review submitted!", "success")
    return redirect(url_for('product_detail', product_id=product_id))



































# ================================= RUN APP ====================================
if __name__ == "__main__":
    print("Starting Witress on http://localhost:5000")
    serve(app, host="0.0.0.0", port=5000)
