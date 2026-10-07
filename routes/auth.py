from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from extensions import db
from models.user import User
from models.student import Student


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "warning")
            return render_template("register.html")

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id
        )

        db.session.add(student)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    logout_user()

    flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))