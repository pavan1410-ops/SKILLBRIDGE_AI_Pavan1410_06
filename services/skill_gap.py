# =========================================================
# SKILLBRIDGE AI
# SKILL GAP ANALYSIS SERVICE
# =========================================================

from services.career_recommender import (
    CAREER_PROFILES,
    get_student_skills
)

from services.learning_progress import (
    get_student_learning_progress
)


# =========================================================
# NORMALIZE SKILL NAME
# =========================================================

def _normalize_skill_name(skill_name):
    """
    Normalize skill names so that different capitalization
    and extra spaces do not cause matching problems.

    Example:

        "Communication"
        "communication"
        " COMMUNICATION "

    all become:

        "communication"
    """

    return str(
        skill_name or ""
    ).strip().lower()


# =========================================================
# SAFE INTEGER
# =========================================================

def _safe_int(value, default=0):

    try:

        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError
    ):

        return default


# =========================================================
# GET LEARNING EVIDENCE
# =========================================================

def get_learning_evidence(student):
    """
    Get the highest learning-progress percentage for
    each skill from the student's completed/in-progress
    courses.

    Example:

        Communication → 100
        Python → 80
        SQL → 60
    """

    evidence = {}

    try:

        learning_progress = (
            get_student_learning_progress(student)
        )

    except Exception:

        learning_progress = []

    if not learning_progress:
        return evidence

    for progress in learning_progress:

        skill_name = _normalize_skill_name(
            getattr(
                progress,
                "skill",
                ""
            )
        )

        if not skill_name:
            continue

        progress_percentage = _safe_int(
            getattr(
                progress,
                "progress_percentage",
                0
            )
        )

        progress_percentage = max(
            0,
            min(
                100,
                progress_percentage
            )
        )

        # -------------------------------------------------
        # If multiple courses exist for the same skill,
        # use the highest learning evidence.
        # -------------------------------------------------

        existing_value = evidence.get(
            skill_name,
            0
        )

        if progress_percentage > existing_value:

            evidence[skill_name] = (
                progress_percentage
            )

    return evidence


# =========================================================
# GET EFFECTIVE STUDENT SKILLS
# =========================================================

def get_effective_student_skills(student):
    """
    Combine:

        1. Student Skill Proficiency
        2. Learning Progress Evidence

    Effective level is the higher of the two.

    Example:

        Student Skill:
            Communication = 0

        Learning Progress:
            Communication = 100%

        Effective Skill:
            Communication = 100
    """

    # -----------------------------------------------------
    # Student-entered / profile skill levels
    # -----------------------------------------------------

    try:

        student_skills = get_student_skills(
            student
        )

    except Exception:

        student_skills = {}

    if student_skills is None:
        student_skills = {}

    normalized_skills = {}

    for skill_name, value in student_skills.items():

        normalized_name = _normalize_skill_name(
            skill_name
        )

        if not normalized_name:
            continue

        skill_level = _safe_int(
            value
        )

        skill_level = max(
            0,
            min(
                100,
                skill_level
            )
        )

        normalized_skills[normalized_name] = (
            skill_level
        )

    # -----------------------------------------------------
    # Learning evidence
    # -----------------------------------------------------

    learning_evidence = get_learning_evidence(
        student
    )

    # -----------------------------------------------------
    # Merge learning evidence
    # -----------------------------------------------------

    for skill_name, evidence_level in (
        learning_evidence.items()
    ):

        current_level = normalized_skills.get(
            skill_name,
            0
        )

        normalized_skills[skill_name] = max(
            current_level,
            evidence_level
        )

    return normalized_skills


# =========================================================
# CALCULATE SKILL GAPS
# =========================================================

def calculate_skill_gaps(student, career):

    career_data = CAREER_PROFILES.get(
        career
    )

    if career_data is None:
        return []

    required_skills = career_data.get(
        "skills",
        {}
    )

    # =====================================================
    # GET EFFECTIVE SKILLS
    # =====================================================

    normalized_student_skills = (
        get_effective_student_skills(student)
    )

    gaps = []

    # =====================================================
    # CALCULATE EACH REQUIRED SKILL
    # =====================================================

    for skill_name, required_level in (
        required_skills.items()
    ):

        normalized_skill_name = (
            _normalize_skill_name(
                skill_name
            )
        )

        current_level = (
            normalized_student_skills.get(
                normalized_skill_name,
                0
            )
        )

        current_level = _safe_int(
            current_level
        )

        required_level = _safe_int(
            required_level
        )

        current_level = max(
            0,
            min(
                100,
                current_level
            )
        )

        required_level = max(
            0,
            min(
                100,
                required_level
            )
        )

        # =================================================
        # GAP
        # =================================================

        gap = max(
            0,
            required_level - current_level
        )

        # =================================================
        # SKILL PERCENTAGE
        # =================================================

        if required_level > 0:

            percentage = round(
                (
                    current_level /
                    required_level
                ) * 100,
                2
            )

        else:

            percentage = 100

        percentage = max(
            0,
            min(
                100,
                percentage
            )
        )

        # =================================================
        # STATUS
        # =================================================

        if current_level >= required_level:

            status = "Strong"

        elif current_level >= (
            required_level * 0.75
        ):

            status = "Good"

        elif current_level >= (
            required_level * 0.50
        ):

            status = "Needs Improvement"

        else:

            status = "Beginner"

        # =================================================
        # PRIORITY
        # =================================================

        priority = get_priority(
            gap
        )

        # =================================================
        # RESULT
        # =================================================

        gaps.append({

            "skill": skill_name,

            "current": current_level,

            "required": required_level,

            "gap": gap,

            "percentage": percentage,

            "status": status,

            "priority": priority

        })

    # =====================================================
    # SORT BY LARGEST GAP
    # =====================================================

    gaps.sort(
        key=lambda item: item["gap"],
        reverse=True
    )

    return gaps


# =========================================================
# PRIORITY
# =========================================================

def get_priority(gap):

    if isinstance(gap, dict):

        gap_value = gap.get(
            "gap",
            0
        )

    else:

        gap_value = gap

    gap_value = _safe_int(
        gap_value
    )

    if gap_value <= 10:

        return "Low"

    elif gap_value <= 25:

        return "Medium"

    elif gap_value <= 50:

        return "High"

    else:

        return "Critical"


# =========================================================
# PRIORITIZED GAPS
# =========================================================

def get_prioritized_gaps(student, career):

    gaps = calculate_skill_gaps(
        student,
        career
    )

    # Only skills that still need improvement

    gaps = [
        item
        for item in gaps
        if item["gap"] > 0
    ]

    priority_order = {

        "Critical": 1,

        "High": 2,

        "Medium": 3,

        "Low": 4

    }

    gaps.sort(
        key=lambda item: (
            priority_order.get(
                item.get(
                    "priority"
                ),
                5
            ),
            -item.get(
                "gap",
                0
            )
        )
    )

    return gaps


# =========================================================
# SUMMARY
# =========================================================

def get_skill_gap_summary(gaps):

    if not gaps:

        return {

            "total_skills": 0,

            "strong_skills": 0,

            "skills_to_improve": 0,

            "critical_gaps": 0,

            "average_gap": 0,

            "completion": 0

        }

    total_skills = len(
        gaps
    )

    strong_skills = sum(

        1

        for item in gaps

        if item["gap"] == 0

    )

    skills_to_improve = sum(

        1

        for item in gaps

        if item["gap"] > 0

    )

    critical_gaps = sum(

        1

        for item in gaps

        if item["priority"] == "Critical"

    )

    total_gap = sum(

        item["gap"]

        for item in gaps

    )

    average_gap = round(

        total_gap /
        total_skills,

        2

    )

    total_percentage = sum(

        item["percentage"]

        for item in gaps

    )

    completion = round(

        total_percentage /
        total_skills,

        2

    )

    return {

        "total_skills": total_skills,

        "strong_skills": strong_skills,

        "skills_to_improve": skills_to_improve,

        "critical_gaps": critical_gaps,

        "average_gap": average_gap,

        "completion": completion

    }


# =========================================================
# TOP SKILL GAPS
# =========================================================

def get_top_skill_gaps(
    student,
    career,
    limit=5
):

    gaps = get_prioritized_gaps(
        student,
        career
    )

    return gaps[:limit]


# =========================================================
# COMPLETED SKILLS
# =========================================================

def get_completed_skills(
    student,
    career
):

    gaps = calculate_skill_gaps(
        student,
        career
    )

    return [

        item

        for item in gaps

        if item["gap"] == 0

    ]