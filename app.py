from flask import Flask, redirect, url_for

from config import Config
from extensions import db, login_manager

from models.user import User
from models.student import Student
from models.skill import Skill
from models.student_skill import StudentSkill
from models.learning_progress import LearningProgress
from models.certificate import Certificate

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.student import student_bp


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # =====================================================
    # CONFIGURATION
    # =====================================================

    app.config.from_object(Config)

    # =====================================================
    # EXTENSIONS
    # =====================================================

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # =====================================================
    # BLUEPRINTS
    # =====================================================

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)

    # =====================================================
    # USER LOADER
    # =====================================================

    @login_manager.user_loader
    def load_user(user_id):

        try:
            return db.session.get(
                User,
                int(user_id)
            )
        except (TypeError, ValueError):
            return None

    # =====================================================
    # HOME
    # =====================================================

    @app.route("/")
    def home():

        return redirect(
            url_for("auth.login")
        )

    # =====================================================
    # CREATE DATABASE TABLES
    # =====================================================

    with app.app_context():
        db.create_all()

    # =====================================================
    # PRINT REGISTERED ROUTES
    # =====================================================

    print("\n========================================")
    print("       SKILLBRIDGE AI ROUTES")
    print("========================================")

    for rule in app.url_map.iter_rules():
        print(
            f"{rule.methods}  {rule}"
        )

    print("========================================\n")

    return app


if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )