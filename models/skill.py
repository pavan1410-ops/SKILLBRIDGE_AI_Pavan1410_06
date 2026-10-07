from extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    category = db.Column(
        db.String(100)
    )

    student_skills = db.relationship(
        "StudentSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )