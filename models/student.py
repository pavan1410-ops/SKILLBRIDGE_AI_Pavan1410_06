# =========================================================
# SKILLBRIDGE AI
# STUDENT MODEL
# =========================================================

from extensions import db


class Student(db.Model):

    __tablename__ = "students"


    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # =====================================================
    # USER RELATIONSHIP
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )


    # =====================================================
    # EDUCATION DETAILS
    # =====================================================

    education = db.Column(
        db.String(100)
    )

    degree = db.Column(
        db.String(100)
    )

    branch = db.Column(
        db.String(100)
    )

    college = db.Column(
        db.String(150)
    )

    graduation_year = db.Column(
        db.Integer
    )


    # =====================================================
    # EXPERIENCE
    # =====================================================

    experience_level = db.Column(
        db.String(50)
    )


    # =====================================================
    # LOCATION
    # =====================================================

    location = db.Column(
        db.String(100)
    )


    # =====================================================
    # LINKEDIN
    # =====================================================

    linkedin_url = db.Column(
        db.String(300)
    )


    # =====================================================
    # USER RELATIONSHIP
    # =====================================================

    user = db.relationship(
        "User",
        back_populates="student"
    )


    # =====================================================
    # STUDENT SKILLS
    #
    # StudentSkill already uses:
    #
    # student = db.relationship(
    #     "Student",
    #     backref=...
    # )
    #
    # Therefore we keep this relationship compatible
    # with the existing StudentSkill model.
    # =====================================================

    skills = db.relationship(
        "StudentSkill",
        back_populates="student",
        cascade="all, delete-orphan"
    )


    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Student {self.id} - "
            f"User {self.user_id}>"
        )