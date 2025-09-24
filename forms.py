# Importing Flask-WTF extension for form handling
from flask_wtf import FlaskForm

# Importing field types for forms
from wtforms import StringField, PasswordField, SubmitField

# Importing validation classes for form validation
from wtforms.validators import InputRequired, Length, Email, Regexp


# ============================ REGISTER FORM ============================

class RegisterForm(FlaskForm):
    """
    This form handles user registration.
    It takes username, email, and password as inputs with proper validation.
    """

    # Username field
    username = StringField(
        "Username",  # Label for the field in the form UI
        validators=[
            InputRequired(message="Username is required."),  # Ensures field is not empty
            Length(min=4, max=50, message="Username must be between 4 and 50 characters."),  # Validates length
            Regexp(
                r'^[A-Za-z0-9_]+$',  # Regex for allowed characters
                message="Username must contain only letters, numbers, or underscores."  # Custom error message
            )
        ]
    )

    # Email field
    email = StringField(
        "Email",  # Label for the field
        validators=[
            InputRequired(message="Email is required."),  # Field must not be empty
            Email(message="Enter a valid email address."),  # Ensures proper email format
            Length(max=100, message="Email must be less than 100 characters.")  # Email length restriction
        ]
    )

    # Password field
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),  # Field must not be empty
            Length(min=6, message="Password must be at least 6 characters."),  # Minimum password length
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$',  
                # Regex to ensure password has at least:
                # - one letter
                # - one number
                # - optional special characters
                message="Password must include both letters and numbers."
            )
        ]
    )

    # Submit button for form submission
    submit = SubmitField("Register")


# ============================ LOGIN FORM ============================

class LoginForm(FlaskForm):
    """
    This form handles user login.
    It requires email and password for authentication.
    """

    # Email field for login
    email = StringField(
        "Email",
        validators=[
            InputRequired(message="Email is required."),  # Field must not be empty
            Email(message="Enter a valid email address."),  # Must be a valid email format
            Length(max=100, message="Email must be less than 100 characters.")  # Max character limit
        ]
    )

    # Password field for login
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),  # Cannot be left empty
            Length(min=6, message="Password must be at least 6 characters.")  # Minimum password length
        ]
    )

    # Submit button for logging in
    submit = SubmitField("Login")
