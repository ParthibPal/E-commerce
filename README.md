# 🛍️ E-Commerce Flask App – Setup & Live Guide

Welcome to the **E-Commerce Flask App**, a full-featured web application built with Flask, MongoDB, and Razorpay integration. Whether you're an admin managing products or a user browsing and shopping, this guide will help you set up the project locally and understand how to use all its features — with clear separation between admin and user roles.

Explore the live app here: [https://e-commerce-kfpr.onrender.com](https://e-commerce-kfpr.onrender.com)


## ⚙️ Setup Instructions

### 1. Enable Script Permissions (Windows Only)

If you're on **Windows** and using **PowerShell**, run this command to allow virtual environment activation:

```bash
powershell Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Create Virtual Environment

Next, create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

* **Windows**:

  ```bash
  venv\Scripts\activate
  ```

* **Mac/Linux**:

  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

Ensure you're in the project root directory, then run the following to install all required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

To start the Flask application locally, run:

```bash
python app.py
```

The app will be accessible at `http://localhost:5000`.

---

## 👨‍💼 Admin Usage Flow

### 1. Access Admin Dashboard

Visit the **Admin Dashboard** by navigating to:

```
http://localhost:5000/dashboard
```

### 2. Log in with Admin Credentials

Log in with your admin credentials.

### 3. Add Products

Use the **Admin Dashboard** interface to add product details and upload images.

### 4. Logout Immediately After Admin Tasks

For security and to prevent session conflicts with user flows, **always log out** after performing admin tasks.

---

## 👤 User Usage Flow

### 1. Register a New User

Visit the registration page at:

```
/register
```

Fill in your **username**, **email**, and **password** to create an account.

### 2. Log In as a User

Visit the login page at:

```
/login
```

### 3. User Features

After logging in as a user, you can access features like:

* **View products**
* **Add items to cart**
* **Checkout**
* **Submit product reviews**
* **Check updated products** (Newly added products by admin will appear in the user interface)

---

## 🚨 Important Notes

### 1. Admin and User Roles Must Remain Isolated

* Admin should always log out before switching to user mode.
* Avoid accessing user routes while logged in as admin to prevent session conflicts.

### 2. Session Conflicts

* If the admin accesses user routes without logging out, it may cause cart/order issues.

### 3. Role-Based Access

* Admins should only interact with `/dashboard` and related management routes.
* Users should only interact with routes like `/cart`, `/checkout`, `/orders`, etc.

---

## 📦 Dependencies

Ensure the following dependencies are installed:

* **Alembic**: 1.16.5
* **Blinker**: 1.9.0
* **Click**: 8.2.1
* **Colorama**: 3.1.1
* **Dnspython**: 2.8.0
* **Email-validator**: 2.3.0
* **Gunicorn**: 23.0.0
* **Idna**: 4.0.5
* **Ttsdangerous**: 2.2.0
* **Jinja2**: 3.1.6
* **Flask**: 3.0.0
* **Flask-Login**: 0.6.3
* **Flask-WTF**: 1.2.1
* **Flask-SQLAlchemy**: 3.1.1
* **WTForms**: 3.1.1
* **email-validator**: 2.0.0.post2
* **Flask-Migrate**: 4.0.5

---

## 💡 Troubleshooting

* If you encounter any issues related to session conflicts, double-check that you’ve logged out from admin before accessing user routes.
* Make sure all dependencies are correctly installed using the `pip install -r requirements.txt` command.

---

Feel free to fork, clone, and customize this project as needed! Happy coding! 😄

=======
# E-commerce
A Flask-based e-commerce web application with product search, user authentication, cart management, payment and a responsive Bootstrap-powered interface.
>>>>>>> b27f3001286831aa2abb72d85d7152cf58971d8b
**
