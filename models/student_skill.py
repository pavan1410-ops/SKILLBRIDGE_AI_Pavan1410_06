from extensions import db


class StudentSkill(db.Model):
    __tablename__ = "student_skills"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.id"),
        nullable=False
    )

    proficiency = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # How the student learned the skill
    source = db.Column(
        db.String(50),
        default="Self-Learned",
        nullable=False
    )

    # Relationship to Student
    student = db.relationship(
        "Student",
        backref=db.backref(
            "student_skills",
            lazy=True
        )
    )

    # Relationship to Skill
    # IMPORTANT:
    # No backref is created here because
    # Skill already has a student_skills relationship.
    skill = db.relationship(
        "Skill"
    )

    def __repr__(self):
        return (
            f"<StudentSkill "
            f"{self.student_id} - "
            f"{self.skill_id} - "
            f"{self.proficiency}%>"
        )