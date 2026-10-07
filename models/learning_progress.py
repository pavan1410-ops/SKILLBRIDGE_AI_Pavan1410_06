# =========================================================
# SKILLBRIDGE AI
# LEARNING PROGRESS MODEL
# =========================================================

from datetime import datetime

from extensions import db


class LearningProgress(db.Model):

    __tablename__ = "learning_progress"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    skill = db.Column(
        db.String(100),
        nullable=False
    )

    course_name = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Not Started",
        nullable=False
    )

    progress_percentage = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    started_at = db.Column(
        db.DateTime,
        nullable=True
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    student = db.relationship(
        "Student",
        backref=db.backref(
            "learning_progress",
            lazy=True
        )
    )

    def __repr__(self):

        return (
            f"<LearningProgress "
            f"{self.skill} - "
            f"{self.progress_percentage}%>"
        )