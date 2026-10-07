# =========================================================
# SKILLBRIDGE AI
# CERTIFICATE MODEL
# =========================================================

from datetime import datetime

from extensions import db


class Certificate(db.Model):

    __tablename__ = "certificates"


    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # =====================================================
    # STUDENT
    # =====================================================

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )


    # =====================================================
    # CERTIFICATE INFORMATION
    # =====================================================

    certificate_name = db.Column(
        db.String(200),
        nullable=False
    )

    course_name = db.Column(
        db.String(200),
        nullable=False
    )

    issuing_organization = db.Column(
        db.String(200),
        nullable=True
    )


    # =====================================================
    # CERTIFICATE TYPE
    # =====================================================

    certificate_type = db.Column(
        db.String(50),
        nullable=False,
        default="Course Certificate"
    )


    # =====================================================
    # FILE INFORMATION
    # =====================================================

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )


    # =====================================================
    # TIMESTAMP
    # =====================================================

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    # =====================================================
    # RELATIONSHIP
    #
    # This creates:
    #
    # student.certificates
    #
    # Do NOT add another certificates relationship
    # inside Student.
    # =====================================================

    student = db.relationship(
        "Student",
        backref=db.backref(
            "certificates",
            lazy=True
        )
    )


    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Certificate "
            f"{self.certificate_name}>"
        )