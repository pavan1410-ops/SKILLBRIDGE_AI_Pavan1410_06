from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.student import Student

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Get the logged-in student's profile
    student = Student.query.filter_by(user_id=current_user.id).first()

    # If profile does not exist yet, create a basic one
    if student is None:
        student = Student(
            user_id=current_user.id,
            name=current_user.username if hasattr(current_user, "username") else ""
        )

        from extensions import db
        db.session.add(student)
        db.session.commit()

    return render_template(
        "dashboard.html",
        user=current_user,
        student=student
    )