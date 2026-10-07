# =========================================================
# SKILLBRIDGE AI
# STUDENT ROUTES
# =========================================================

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    jsonify,
    send_file
)

from flask_login import (
    login_required,
    current_user
)

from urllib.parse import urlparse

import csv
import io
import os

from werkzeug.utils import secure_filename

from extensions import db

from models.student import Student
from models.skill import Skill
from models.student_skill import StudentSkill
from models.certificate import Certificate


# =========================================================
# SERVICES
# =========================================================

from services.career_recommender import (
    recommend_careers,
    get_career_profile
)

from services.skill_gap import (
    calculate_skill_gaps,
    get_skill_gap_summary,
    get_top_skill_gaps,
    get_completed_skills
)

from services.learning_path import (
    generate_learning_path,
    create_complete_roadmap
)

from services.readiness import (
    get_readiness_details
)

from services.digital_twin import (
    build_digital_twin
)

from services.job_matcher import (
    match_job
)

from services.what_if import (
    get_what_if_options,
    simulate_career, get_next_learning_recommendation
)

from services.powerbi_export import (
    generate_powerbi_tables
)

from services.learning_progress import (
    get_or_create_learning_item,
    get_student_learning_progress,
    get_learning_summary,
    update_learning_progress
)
from services.what_if import (
    get_what_if_options,
    simulate_career
)

# =========================================================
# BLUEPRINT
# =========================================================

student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/student"
)


# =========================================================
# CONSTANTS
# =========================================================

CERTIFICATE_UPLOAD_FOLDER = os.path.join(
    "static",
    "uploads",
    "certificates"
)

ALLOWED_CERTIFICATE_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}


# =========================================================
# HELPER
# GET OR CREATE STUDENT
# =========================================================

def get_or_create_student():

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    if student is None:

        student = Student(
            user_id=current_user.id
        )

        db.session.add(student)

        db.session.commit()

    return student


# =========================================================
# HELPER
# LINKEDIN URL VALIDATION
# =========================================================

def is_valid_linkedin_url(url):

    if not url:
        return True

    url = url.strip()

    try:

        parsed = urlparse(url)

        if parsed.scheme not in {
            "http",
            "https"
        }:

            return False

        hostname = (
            parsed.hostname or ""
        ).lower()

        allowed_hosts = {
            "linkedin.com",
            "www.linkedin.com"
        }

        if hostname not in allowed_hosts:

            return False

        if not parsed.path.lower().startswith(
            "/in/"
        ):

            return False

        return True

    except Exception:

        return False


# =========================================================
# HELPER
# CERTIFICATE FILE EXTENSION
# =========================================================

def allowed_certificate_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename.rsplit(
            ".",
            1
        )[1]
        .lower()
    )

    return extension in ALLOWED_CERTIFICATE_EXTENSIONS


# =========================================================
# PROFILE
# =========================================================

@student_bp.route(
    "/profile",
    methods=["GET", "POST"]
)
@login_required
def profile():

    student = get_or_create_student()

    if request.method == "POST":

        # -------------------------------------------------
        # BASIC PROFILE
        # -------------------------------------------------

        student.education = request.form.get(
            "education",
            ""
        ).strip()

        student.degree = request.form.get(
            "degree",
            ""
        ).strip()

        student.branch = request.form.get(
            "branch",
            ""
        ).strip()

        student.college = request.form.get(
            "college",
            ""
        ).strip()

        # -------------------------------------------------
        # GRADUATION YEAR
        # -------------------------------------------------

        graduation_year = request.form.get(
            "graduation_year",
            ""
        ).strip()

        if graduation_year:

            try:

                student.graduation_year = int(
                    graduation_year
                )

            except (
                TypeError,
                ValueError
            ):

                student.graduation_year = None

        else:

            student.graduation_year = None

        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        student.experience_level = request.form.get(
            "experience_level",
            ""
        ).strip()

        student.location = request.form.get(
            "location",
            ""
        ).strip()

        # -------------------------------------------------
        # LINKEDIN
        # -------------------------------------------------

        linkedin_url = request.form.get(
            "linkedin_url",
            ""
        ).strip()

        if linkedin_url and not is_valid_linkedin_url(
            linkedin_url
        ):

            flash(
                "Please enter a valid LinkedIn profile URL.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.profile"
                )
            )

        student.linkedin_url = (
            linkedin_url
            if linkedin_url
            else None
        )

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for(
                "student.profile"
            )
        )

    return render_template(
        "profile.html",
        student=student,
        user=current_user
    )


# =========================================================
# SKILLS
# =========================================================

@student_bp.route(
    "/skills",
    methods=["GET", "POST"]
)
@login_required
def skills():

    student = get_or_create_student()

    if request.method == "POST":

        # -------------------------------------------------
        # SKILL NAME
        # -------------------------------------------------

        skill_name = request.form.get(
            "skill",
            ""
        ).strip()

        if not skill_name:

            skill_name = request.form.get(
                "skill_name",
                ""
            ).strip()

        # -------------------------------------------------
        # PROFICIENCY
        # -------------------------------------------------

        proficiency = request.form.get(
            "proficiency",
            "0"
        ).strip()

        try:

            proficiency = int(
                proficiency
            )

        except (
            TypeError,
            ValueError
        ):

            proficiency = 0

        proficiency = max(
            0,
            min(
                100,
                proficiency
            )
        )

        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        source = request.form.get(
            "source",
            "Self-Learned"
        ).strip()

        if not source:

            source = "Self-Learned"

        allowed_sources = {
            "Self-Learned",
            "Online Course",
            "College / Academic",
            "Certification",
            "Project",
            "Internship",
            "Other"
        }

        if source not in allowed_sources:

            source = "Self-Learned"

        # -------------------------------------------------
        # VALIDATE
        # -------------------------------------------------

        if not skill_name:

            flash(
                "Please enter a skill.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.skills"
                )
            )

        # -------------------------------------------------
        # FIND SKILL
        # -------------------------------------------------

        skill = Skill.query.filter(
            db.func.lower(Skill.name)
            ==
            skill_name.lower()
        ).first()

        # -------------------------------------------------
        # CREATE SKILL
        # -------------------------------------------------

        if skill is None:

            skill = Skill(
                name=skill_name,
                category="Technical"
            )

            db.session.add(
                skill
            )

            db.session.flush()

        # -------------------------------------------------
        # FIND STUDENT SKILL
        # -------------------------------------------------

        existing = StudentSkill.query.filter_by(
            student_id=student.id,
            skill_id=skill.id
        ).first()

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        if existing:

            existing.proficiency = proficiency
            existing.source = source

            flash(
                f"{skill.name} updated successfully!",
                "success"
            )

        # -------------------------------------------------
        # ADD
        # -------------------------------------------------

        else:

            student_skill = StudentSkill(
                student_id=student.id,
                skill_id=skill.id,
                proficiency=proficiency,
                source=source
            )

            db.session.add(
                student_skill
            )

            flash(
                f"{skill.name} added successfully!",
                "success"
            )

        db.session.commit()

        return redirect(
            url_for(
                "student.skills"
            )
        )

    # -----------------------------------------------------
    # GET SKILLS
    # -----------------------------------------------------

    student_skills = (
        StudentSkill.query
        .filter_by(
            student_id=student.id
        )
        .order_by(
            StudentSkill.id.asc()
        )
        .all()
    )

    return render_template(
        "skills.html",
        student=student,
        student_skills=student_skills,
        user=current_user
    )


# =========================================================
# DELETE STUDENT SKILL
# =========================================================

@student_bp.route(
    "/skills/delete/<int:student_skill_id>",
    methods=["POST"]
)
@login_required
def delete_skill(student_skill_id):

    student = get_or_create_student()

    student_skill = StudentSkill.query.filter_by(
        id=student_skill_id,
        student_id=student.id
    ).first()

    if student_skill is None:

        flash(
            "Skill not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.skills"
            )
        )

    skill_name = (
        student_skill.skill.name
        if student_skill.skill
        else "Skill"
    )

    db.session.delete(
        student_skill
    )

    db.session.commit()

    flash(
        f"{skill_name} removed from your skills.",
        "success"
    )

    return redirect(
        url_for(
            "student.skills"
        )
    )


# =========================================================
# CERTIFICATES
# =========================================================

@student_bp.route(
    "/certificates",
    methods=["GET", "POST"]
)
@login_required
def certificates():

    student = get_or_create_student()

    # -----------------------------------------------------
    # CREATE UPLOAD DIRECTORY
    # -----------------------------------------------------

    os.makedirs(
        CERTIFICATE_UPLOAD_FOLDER,
        exist_ok=True
    )

    # =====================================================
    # UPLOAD CERTIFICATE
    # =====================================================

    if request.method == "POST":

        certificate_name = request.form.get(
            "certificate_name",
            ""
        ).strip()

        course_name = request.form.get(
            "course_name",
            ""
        ).strip()

        issuing_organization = request.form.get(
            "issuing_organization",
            ""
        ).strip()

        certificate_type = request.form.get(
            "certificate_type",
            "Course Certificate"
        ).strip()

        certificate_file = request.files.get(
            "certificate_file"
        )

        # -------------------------------------------------
        # COURSE CERTIFICATE ONLY
        # -------------------------------------------------

        if certificate_type != "Course Certificate":

            flash(
                "Only course certificates can be uploaded.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # CERTIFICATE NAME
        # -------------------------------------------------

        if not certificate_name:

            flash(
                "Certificate name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # COURSE NAME
        # -------------------------------------------------

        if not course_name:

            flash(
                "Course name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # FILE
        # -------------------------------------------------

        if certificate_file is None:

            flash(
                "Please select a certificate file.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        original_filename = (
            certificate_file.filename
        )

        if not original_filename:

            flash(
                "Invalid certificate file.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # EXTENSION VALIDATION
        # -------------------------------------------------

        if not allowed_certificate_file(
            original_filename
        ):

            flash(
                "Only PDF, PNG, JPG and JPEG "
                "certificate files are allowed.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # SECURE FILENAME
        # -------------------------------------------------

        safe_filename = secure_filename(
            original_filename
        )

        if not safe_filename:

            flash(
                "Invalid certificate filename.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.certificates"
                )
            )

        # -------------------------------------------------
        # PREVENT DUPLICATE FILENAMES
        # -------------------------------------------------

        base_name, file_extension = os.path.splitext(
            safe_filename
        )

        final_filename = safe_filename

        counter = 1

        while os.path.exists(
            os.path.join(
                CERTIFICATE_UPLOAD_FOLDER,
                final_filename
            )
        ):

            final_filename = (
                f"{base_name}_{counter}"
                f"{file_extension}"
            )

            counter += 1

        # -------------------------------------------------
        # FINAL FILE PATH
        # -------------------------------------------------

        file_path = os.path.join(
            CERTIFICATE_UPLOAD_FOLDER,
            final_filename
        )

        # -------------------------------------------------
        # SAVE FILE
        # -------------------------------------------------

        certificate_file.save(
            file_path
        )

        # -------------------------------------------------
        # DATABASE RECORD
        # -------------------------------------------------

        certificate = Certificate(
            student_id=student.id,
            certificate_name=certificate_name,
            course_name=course_name,
            issuing_organization=(
                issuing_organization
                if issuing_organization
                else None
            ),
            certificate_type="Course Certificate",
            file_name=final_filename,
            file_path=file_path
        )

        db.session.add(
            certificate
        )

        db.session.commit()

        flash(
            "Course certificate uploaded successfully!",
            "success"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    # =====================================================
    # GET CERTIFICATES
    # =====================================================

    certificates = (
        Certificate.query
        .filter_by(
            student_id=student.id
        )
        .order_by(
            Certificate.uploaded_at.desc()
        )
        .all()
    )

    return render_template(
        "certificates.html",
        student=student,
        certificates=certificates,
        user=current_user
    )


# =========================================================
# VIEW CERTIFICATE
# =========================================================

@student_bp.route(
    "/certificates/view/<int:certificate_id>"
)
@login_required
def view_certificate(certificate_id):

    student = get_or_create_student()

    certificate = Certificate.query.filter_by(
        id=certificate_id,
        student_id=student.id
    ).first()

    if certificate is None:

        flash(
            "Certificate not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    if not os.path.exists(
        certificate.file_path
    ):

        flash(
            "Certificate file could not be found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    return send_file(
        certificate.file_path,
        as_attachment=False
    )


# =========================================================
# DOWNLOAD CERTIFICATE
# =========================================================

@student_bp.route(
    "/certificates/download/<int:certificate_id>"
)
@login_required
def download_certificate(certificate_id):

    student = get_or_create_student()

    certificate = Certificate.query.filter_by(
        id=certificate_id,
        student_id=student.id
    ).first()

    if certificate is None:

        flash(
            "Certificate not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    if not os.path.exists(
        certificate.file_path
    ):

        flash(
            "Certificate file could not be found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    return send_file(
        certificate.file_path,
        as_attachment=True,
        download_name=certificate.file_name
    )


# =========================================================
# DELETE CERTIFICATE
# =========================================================

@student_bp.route(
    "/certificates/delete/<int:certificate_id>",
    methods=["POST"]
)
@login_required
def delete_certificate(certificate_id):

    student = get_or_create_student()

    certificate = Certificate.query.filter_by(
        id=certificate_id,
        student_id=student.id
    ).first()

    if certificate is None:

        flash(
            "Certificate not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.certificates"
            )
        )

    # -----------------------------------------------------
    # DELETE PHYSICAL FILE
    # -----------------------------------------------------

    if certificate.file_path:

        try:

            if os.path.exists(
                certificate.file_path
            ):

                os.remove(
                    certificate.file_path
                )

        except OSError:

            pass

    # -----------------------------------------------------
    # DELETE DATABASE RECORD
    # -----------------------------------------------------

    db.session.delete(
        certificate
    )

    db.session.commit()

    flash(
        "Certificate deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "student.certificates"
        )
    )


# =========================================================
# CAREER RECOMMENDATIONS
# =========================================================

@student_bp.route(
    "/careers"
)
@login_required
def careers():

    student = get_or_create_student()

    recommendations = recommend_careers(
        student
    )

    return render_template(
        "careers.html",
        student=student,
        recommendations=recommendations,
        user=current_user
    )


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

@student_bp.route(
    "/skill-gap/<path:career>"
)
@login_required
def skill_gap(career):

    student = get_or_create_student()

    career_profile = get_career_profile(
        career
    )

    if career_profile is None:

        flash(
            "Career profile not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.careers"
            )
        )

    gaps = calculate_skill_gaps(
        student,
        career
    )

    if gaps is None:
        gaps = []

    summary = get_skill_gap_summary(
        gaps
    )

    if summary is None:
        summary = {}

    top_gaps = get_top_skill_gaps(
        student,
        career,
        limit=5
    )

    if top_gaps is None:
        top_gaps = []

    completed_skills = get_completed_skills(
        student,
        career
    )

    if completed_skills is None:
        completed_skills = []

    return render_template(
        "skill_gap.html",
        student=student,
        career=career,
        career_profile=career_profile,
        gaps=gaps,
        summary=summary,
        top_gaps=top_gaps,
        completed_skills=completed_skills,
        user=current_user
    )


# =========================================================
# CAREER READINESS
# =========================================================

@student_bp.route(
    "/readiness"
)
@login_required
def readiness():

    student = get_or_create_student()

    readiness_data = get_readiness_details(
        student
    )

    return render_template(
        "readiness.html",
        student=student,
        user=current_user,
        score=readiness_data["score"],
        status=readiness_data["status"],
        career=readiness_data["career"],
        skill_breakdown=readiness_data["skill_breakdown"],
        strengths=readiness_data["strengths"],
        improvements=readiness_data["improvements"],
        actions=readiness_data["actions"]
    )


# =========================================================
# PERSONALIZED LEARNING PATH
# =========================================================

@student_bp.route(
    "/learning-path/<path:career>",
    methods=["GET", "POST"]
)
@login_required
def learning_path(career):

    student = get_or_create_student()

    career_profile = get_career_profile(
        career
    )

    if career_profile is None:

        flash(
            "Career profile not found.",
            "danger"
        )

        return redirect(
            url_for(
                "student.careers"
            )
        )

    # =====================================================
    # PROGRESS UPDATE
    # =====================================================

    if request.method == "POST":

        skill = request.form.get(
            "skill",
            ""
        ).strip()

        course_name = request.form.get(
            "course_name",
            ""
        ).strip()

        progress_percentage = request.form.get(
            "progress_percentage",
            "0"
        )

        try:

            progress_percentage = int(
                progress_percentage
            )

        except (
            TypeError,
            ValueError
        ):

            progress_percentage = 0

        progress_percentage = max(
            0,
            min(
                100,
                progress_percentage
            )
        )

        if not skill or not course_name:

            flash(
                "Skill and course name are required.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.learning_path",
                    career=career
                )
            )

        update_learning_progress(
            student,
            skill,
            course_name,
            progress_percentage
        )

        flash(
            "Learning progress updated successfully!",
            "success"
        )

        return redirect(
            url_for(
                "student.learning_path",
                career=career
            )
        )

    # =====================================================
    # GENERATE LEARNING PATH
    # =====================================================

    learning_path_data = generate_learning_path(
        student,
        career
    )

    if learning_path_data is None:
        learning_path_data = []

    roadmap = create_complete_roadmap(
        student,
        career
    )

    if roadmap is None:
        roadmap = []

    # =====================================================
    # CREATE PROGRESS ITEMS
    # =====================================================

    for item in learning_path_data:

        skill = str(
            item.get(
                "skill",
                ""
            )
        ).strip()

        course_name = str(
            item.get(
                "course",
                ""
            )
        ).strip()

        if skill and course_name:

            get_or_create_learning_item(
                student,
                skill,
                course_name
            )

    # =====================================================
    # GET SAVED PROGRESS
    # =====================================================

    learning_progress = (
        get_student_learning_progress(
            student
        )
    )

    if learning_progress is None:
        learning_progress = []

    progress_lookup = {}

    for progress in learning_progress:

        key = (
            str(
                progress.skill
            ).strip().lower(),

            str(
                progress.course_name
            ).strip().lower()
        )

        progress_lookup[key] = progress

    # =====================================================
    # APPLY PROGRESS
    # =====================================================

    for item in learning_path_data:

        skill = str(
            item.get(
                "skill",
                ""
            )
        ).strip()

        course_name = str(
            item.get(
                "course",
                ""
            )
        ).strip()

        progress = progress_lookup.get(
            (
                skill.lower(),
                course_name.lower()
            )
        )

        if progress:

            item["learning_status"] = (
                progress.status
                or "Not Started"
            )

            item["progress_percentage"] = (
                progress.progress_percentage
                or 0
            )

        else:

            item["learning_status"] = (
                "Not Started"
            )

            item["progress_percentage"] = 0

    # =====================================================
    # SUMMARY
    # =====================================================

    learning_summary = get_learning_summary(
        student
    )

    if learning_summary is None:

        learning_summary = {
            "total": 0,
            "completed": 0,
            "in_progress": 0,
            "not_started": 0,
            "average_progress": 0
        }

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "learning_path.html",
        student=student,
        career=career,
        career_profile=career_profile,
        learning_path=learning_path_data,
        roadmap=roadmap,
        learning_progress=learning_progress,
        learning_summary=learning_summary,
        user=current_user
    )


# =========================================================
# AI CAREER DIGITAL TWIN
# =========================================================

@student_bp.route(
    "/digital-twin"
)
@login_required
def digital_twin():

    student = get_or_create_student()

    digital_twin_data = build_digital_twin(
        student
    )

    return render_template(
        "digital_twin.html",
        student=student,
        user=current_user,
        digital_twin_data=digital_twin_data
    )


# =========================================================
# WHAT-IF CAREER SIMULATION
# =========================================================

@student_bp.route(
    "/what-if",
    methods=["GET", "POST"]
)
@login_required
def what_if():

    student = get_or_create_student()

    # =====================================================
    # POST — RUN SIMULATION
    # =====================================================

    if request.method == "POST":

        data = request.get_json(
            silent=True
        ) or {}

        career = (
            data.get("career")
            or ""
        ).strip()

        hypothetical_skills = (
            data.get(
                "hypothetical_skills",
                {}
            )
            or {}
        )

        if not career:

            return jsonify({
                "success": False,
                "error": "Please select a target career."
            }), 400

        if not isinstance(
            hypothetical_skills,
            dict
        ):

            return jsonify({
                "success": False,
                "error": "Invalid simulated skill data."
            }), 400

        cleaned_skills = {}

        for skill_name, level in hypothetical_skills.items():

            skill_name = str(
                skill_name
            ).strip()

            if not skill_name:
                continue

            try:

                level = float(level)

            except (
                TypeError,
                ValueError
            ):

                level = 0

            level = max(
                0,
                min(
                    100,
                    level
                )
            )

            cleaned_skills[
                skill_name
            ] = level

        try:

            result = simulate_career(
                student,
                career,
                cleaned_skills
            )

        except Exception as error:

            return jsonify({
                "success": False,
                "error":
                    f"Simulation failed: {str(error)}"
            }), 500

        if result is None:

            result = {}

        def safe_number(
            value,
            default=0
        ):

            try:

                return float(value)

            except (
                TypeError,
                ValueError
            ):

                return default

        current_match = safe_number(
            result.get(
                "current_match",
                0
            )
        )

        simulated_match = safe_number(
            result.get(
                "simulated_match",
                0
            )
        )

        improvement = (
            simulated_match
            -
            current_match
        )

        remaining_gaps = (
            result.get(
                "remaining_gaps",
                []
            )
            or []
        )

        gap_count = len(
            remaining_gaps
        )

        # =================================================
        # NEXT LEARNING RECOMMENDATION
        # =================================================

        next_learning = (
            get_next_learning_recommendation(
                result
            )
        )

        return jsonify({

            "success":
                True,

            "career":
                career,

            "current_match":
                round(
                    current_match,
                    2
                ),

            "simulated_match":
                round(
                    simulated_match,
                    2
                ),

            "improvement":
                round(
                    improvement,
                    2
                ),

            "gap_count":
                gap_count,

            "remaining_gaps":
                remaining_gaps,

            "current_readiness":
                safe_number(
                    result.get(
                        "current_readiness",
                        0
                    )
                ),

            "simulated_readiness":
                safe_number(
                    result.get(
                        "simulated_readiness",
                        0
                    )
                ),

            "next_learning":
                next_learning
        })

    # =====================================================
    # GET — SHOW SIMULATOR
    # =====================================================

    careers = get_what_if_options(
        student
    )

    if careers is None:
        careers = []

    return render_template(
        "what_if.html",
        student=student,
        user=current_user,
        careers=careers
    )
# =========================================================
# AI JOB MATCHING
# =========================================================

@student_bp.route(
    "/jobs"
)
@login_required
def jobs():

    student = get_or_create_student()

    jobs_data = match_job(
        student
    )

    if jobs_data is None:
        jobs_data = []

    top_jobs = jobs_data[:10]

    total_jobs = len(
        jobs_data
    )

    # -----------------------------------------------------
    # IMPORTANT:
    # job_matcher.py returns "match_percentage"
    # -----------------------------------------------------

    match_values = []

    for job in jobs_data:

        try:

            value = float(
                job.get(
                    "match_percentage",
                    job.get(
                        "match",
                        0
                    )
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            value = 0

        match_values.append(
            value
        )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    if match_values:

        average_match = round(
            sum(match_values)
            /
            len(match_values),
            2
        )

        best_match = round(
            max(match_values),
            2
        )

    else:

        average_match = 0

        best_match = 0

    strong_matches = sum(
        1
        for value in match_values
        if value >= 70
    )

    job_summary = {

        "total_jobs":
            total_jobs,

        "average_match":
            average_match,

        "best_match":
            best_match,

        "strong_matches":
            strong_matches
    }

    return render_template(
        "jobs.html",
        student=student,
        user=current_user,
        jobs=jobs_data,
        top_jobs=top_jobs,
        job_summary=job_summary
    )


# =========================================================
# POWER BI
# CSV HELPER
# =========================================================

def rows_to_csv(rows):

    if not rows:

        return ""

    output = io.StringIO()

    fieldnames = list(
        rows[0].keys()
    )

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        rows
    )

    return output.getvalue()


# =========================================================
# POWER BI
# GENERATE ALL TABLES
# =========================================================

def generate_all_powerbi_tables():

    students = Student.query.order_by(
        Student.id
    ).all()

    all_tables = {

        "StudentAnalytics": [],

        "SkillAnalytics": [],

        "CareerAnalytics": [],

        "SkillGapAnalytics": [],

        "ReadinessAnalytics": []
    }

    for student in students:

        student_tables = generate_powerbi_tables(
            student
        )

        for table_name, rows in student_tables.items():

            if rows:

                all_tables[
                    table_name
                ].extend(
                    rows
                )

    return all_tables


# =========================================================
# POWER BI
# EXPORT TABLE
# =========================================================

@student_bp.route(
    "/export/<table_name>"
)
@login_required
def export_powerbi_table(table_name):

    tables = generate_all_powerbi_tables()

    if table_name not in tables:

        return Response(
            "Invalid Power BI table.",
            status=404,
            mimetype="text/plain"
        )

    csv_data = rows_to_csv(
        tables[table_name]
    )

    filename = (
        f"{table_name}.csv"
    )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename={filename}"
        }
    )


# =========================================================
# POWER BI
# FRIENDLY TABLE NAMES
# =========================================================

POWERBI_TABLE_NAMES = {

    "students":
        "StudentAnalytics",

    "readliness":
        "ReadinessAnalytics",

    "skillgaps":
        "SkillGapAnalytics",

    "careerrecord":
        "CareerAnalytics",

    "studentskills":
        "SkillAnalytics"
}


# =========================================================
# POWER BI
# DOWNLOAD CSV
# =========================================================

@student_bp.route(
    "/powerbi/<table_name>"
)
@login_required
def powerbi_export(table_name):

    internal_table = (
        POWERBI_TABLE_NAMES.get(
            table_name
        )
    )

    if internal_table is None:

        return Response(
            "Invalid Power BI table name.",
            status=404,
            mimetype="text/plain"
        )

    tables = (
        generate_all_powerbi_tables()
    )

    rows = tables.get(
        internal_table,
        []
    )

    csv_data = rows_to_csv(
        rows
    )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename={table_name}.csv"
        }
    )


# =========================================================
# END OF STUDENT ROUTES
# =========================================================