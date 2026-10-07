# =========================================================
# SKILLBRIDGE AI
# CAREER READINESS SERVICE
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
    Normalize skill names for reliable matching.

    Example:

        Communication
        communication
        COMMUNICATION

    all become:

        communication
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

def _get_learning_evidence(student):
    """
    Get the highest learning progress percentage
    for every skill.

    Example:

        Communication → 100
        Python → 80
        SQL → 60
    """

    evidence = {}

    try:

        learning_progress = (
            get_student_learning_progress(
                student
            )
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

        existing_value = evidence.get(
            skill_name,
            0
        )

        # If multiple courses exist for the same
        # skill, keep the highest evidence.

        if progress_percentage > existing_value:

            evidence[skill_name] = (
                progress_percentage
            )

    return evidence


# =========================================================
# NORMALIZE STUDENT SKILLS
# =========================================================

def _get_normalized_student_skills(student):
    """
    Combine:

        1. Student Skill Proficiency
        2. Learning Progress Evidence

    The higher value is used.

    Example:

        Communication skill = 0
        Course progress = 100

        Effective skill = 100
    """

    try:

        student_skills = get_student_skills(
            student
        )

    except Exception:

        student_skills = {}

    if student_skills is None:

        student_skills = {}

    normalized = {}

    # =====================================================
    # 1. STUDENT PROFILE SKILLS
    # =====================================================

    for skill_name, proficiency in (
        student_skills.items()
    ):

        normalized_name = _normalize_skill_name(
            skill_name
        )

        if not normalized_name:

            continue

        proficiency = _safe_int(
            proficiency
        )

        proficiency = max(
            0,
            min(
                100,
                proficiency
            )
        )

        normalized[normalized_name] = (
            proficiency
        )

    # =====================================================
    # 2. LEARNING EVIDENCE
    # =====================================================

    learning_evidence = _get_learning_evidence(
        student
    )

    # =====================================================
    # 3. USE HIGHER VALUE
    # =====================================================

    for skill_name, evidence_level in (
        learning_evidence.items()
    ):

        current_level = normalized.get(
            skill_name,
            0
        )

        normalized[skill_name] = max(
            current_level,
            evidence_level
        )

    return normalized


# =========================================================
# GET BEST CAREER
# =========================================================

def _get_best_career(student):
    """
    Find the career with the highest skill match.

    Learning evidence is included in the calculation.
    """

    if not student:

        return None

    student_skills = (
        _get_normalized_student_skills(
            student
        )
    )

    best_career = None
    best_score = -1

    for career_name, career_data in (
        CAREER_PROFILES.items()
    ):

        requirements = career_data.get(
            "skills",
            {}
        )

        if not requirements:

            continue

        total = 0
        valid_requirements = 0

        for skill_name, required_level in (
            requirements.items()
        ):

            required_level = _safe_int(
                required_level
            )

            if required_level <= 0:

                continue

            normalized_name = (
                _normalize_skill_name(
                    skill_name
                )
            )

            current_level = student_skills.get(
                normalized_name,
                0
            )

            total += min(
                current_level /
                required_level,
                1
            )

            valid_requirements += 1

        if valid_requirements == 0:

            continue

        score = (
            total /
            valid_requirements
        )

        if score > best_score:

            best_score = score

            best_career = career_name

    return best_career


# =========================================================
# CALCULATE READINESS
# =========================================================

def calculate_readiness(
    student,
    career=None
):
    """
    Calculate career readiness from 0 to 100.

    The calculation uses the higher of:

        Student Skill Proficiency
        OR
        Learning Progress Evidence

    Example:

        Communication:
            Student Skill = 0
            Course Progress = 100

        Effective Skill:
            100
    """

    if not student:

        return 0

    # =====================================================
    # GET EFFECTIVE SKILLS
    # =====================================================

    student_skills = (
        _get_normalized_student_skills(
            student
        )
    )

    # =====================================================
    # AUTOMATIC CAREER SELECTION
    # =====================================================

    if career is None:

        career = _get_best_career(
            student
        )

    # =====================================================
    # VALIDATE CAREER
    # =====================================================

    if not career:

        return 0

    career_data = CAREER_PROFILES.get(
        career
    )

    if not career_data:

        return 0

    requirements = career_data.get(
        "skills",
        {}
    )

    if not requirements:

        return 0

    # =====================================================
    # CALCULATE READINESS
    # =====================================================

    total_percentage = 0
    valid_requirements = 0

    for skill_name, required_level in (
        requirements.items()
    ):

        required_level = _safe_int(
            required_level
        )

        if required_level <= 0:

            continue

        normalized_name = (
            _normalize_skill_name(
                skill_name
            )
        )

        current_level = student_skills.get(
            normalized_name,
            0
        )

        percentage = min(
            current_level /
            required_level,
            1
        ) * 100

        total_percentage += percentage

        valid_requirements += 1

    if valid_requirements == 0:

        return 0

    readiness = (
        total_percentage /
        valid_requirements
    )

    return round(
        max(
            0,
            min(
                100,
                readiness
            )
        )
    )


# =========================================================
# READINESS STATUS
# =========================================================

def get_readiness_status(score):
    """
    Convert readiness percentage into a readable status.
    """

    try:

        score = float(
            score or 0
        )

    except (
        TypeError,
        ValueError
    ):

        score = 0

    if score >= 90:

        return "Highly Ready"

    elif score >= 75:

        return "Job Ready"

    elif score >= 60:

        return "Nearly Ready"

    elif score >= 40:

        return "Developing"

    return "Needs Improvement"


# =========================================================
# READINESS LEVEL
# =========================================================

def get_readiness_level(score):
    """
    Return a simple readiness category.
    """

    try:

        score = float(
            score or 0
        )

    except (
        TypeError,
        ValueError
    ):

        score = 0

    if score >= 90:

        return "Excellent"

    elif score >= 75:

        return "Strong"

    elif score >= 60:

        return "Good Progress"

    elif score >= 40:

        return "Developing"

    return "Needs Improvement"


# =========================================================
# READINESS COLOR CLASS
# =========================================================

def get_readiness_color(score):
    """
    Return a CSS-friendly readiness color category.
    """

    try:

        score = float(
            score or 0
        )

    except (
        TypeError,
        ValueError
    ):

        score = 0

    if score >= 90:

        return "excellent"

    elif score >= 75:

        return "ready"

    elif score >= 60:

        return "nearly"

    elif score >= 40:

        return "developing"

    return "needs-improvement"


# =========================================================
# GET CAREER REQUIREMENTS
# =========================================================

def _get_career_requirements(career):
    """
    Return skill requirements for a career.
    """

    if not career:

        return {}

    career_data = CAREER_PROFILES.get(
        career,
        {}
    )

    return career_data.get(
        "skills",
        {}
    )


# =========================================================
# GET SKILL BREAKDOWN
# =========================================================

def get_skill_breakdown(
    student,
    career=None
):
    """
    Return detailed skill-by-skill readiness.

    Learning progress is included as skill evidence.
    """

    if not student:

        return []

    if career is None:

        career = _get_best_career(
            student
        )

    requirements = _get_career_requirements(
        career
    )

    student_skills = (
        _get_normalized_student_skills(
            student
        )
    )

    breakdown = []

    for skill_name, required_level in (
        requirements.items()
    ):

        required_level = _safe_int(
            required_level
        )

        if required_level <= 0:

            continue

        normalized_name = (
            _normalize_skill_name(
                skill_name
            )
        )

        current_level = student_skills.get(
            normalized_name,
            0
        )

        current_level = max(
            0,
            min(
                100,
                current_level
            )
        )

        percentage = min(
            current_level /
            required_level,
            1
        ) * 100

        gap = max(
            required_level -
            current_level,
            0
        )

        # =================================================
        # STATUS
        # =================================================

        if current_level >= required_level:

            status = "Strong"

        elif percentage >= 75:

            status = "Good"

        elif percentage >= 50:

            status = "Developing"

        else:

            status = "Needs Improvement"

        # =================================================
        # PRIORITY
        # =================================================

        if gap >= 50:

            priority = "Critical"

        elif gap >= 30:

            priority = "High"

        elif gap >= 15:

            priority = "Medium"

        elif gap > 0:

            priority = "Low"

        else:

            priority = "None"

        breakdown.append({

            "skill": skill_name,

            "current": current_level,

            "required": required_level,

            "percentage": round(
                percentage,
                2
            ),

            "gap": gap,

            "status": status,

            "priority": priority

        })

    # =====================================================
    # LARGEST GAPS FIRST
    # =====================================================

    breakdown.sort(
        key=lambda item: (
            item["gap"],
            -item["percentage"]
        ),
        reverse=True
    )

    return breakdown


# =========================================================
# GET STRENGTHS
# =========================================================

def get_readiness_strengths(
    student,
    career=None
):
    """
    Return skills where the student is meeting
    or exceeding the career requirement.
    """

    breakdown = get_skill_breakdown(
        student,
        career
    )

    strengths = []

    for item in breakdown:

        if item["current"] >= item["required"]:

            strengths.append(
                item
            )

    return strengths


# =========================================================
# GET IMPROVEMENT AREAS
# =========================================================

def get_readiness_improvements(
    student,
    career=None
):
    """
    Return the most important skills that need
    improvement.
    """

    breakdown = get_skill_breakdown(
        student,
        career
    )

    improvements = [

        item

        for item in breakdown

        if item["gap"] > 0

    ]

    return improvements[:5]


# =========================================================
# GET RECOMMENDED ACTIONS
# =========================================================

def get_recommended_actions(
    student,
    career=None
):
    """
    Generate practical actions based on readiness.
    """

    if not student:

        return []

    score = calculate_readiness(
        student,
        career
    )

    breakdown = get_skill_breakdown(
        student,
        career
    )

    actions = []

    # =====================================================
    # SKILL ACTION
    # =====================================================

    if breakdown:

        largest_gap = max(
            breakdown,
            key=lambda item: item["gap"]
        )

        if largest_gap["gap"] > 0:

            actions.append({

                "icon": "🧩",

                "title": (
                    f"Improve "
                    f"{largest_gap['skill']}"
                ),

                "description": (
                    f"Current proficiency is "
                    f"{largest_gap['current']}%, "
                    f"while the target is "
                    f"{largest_gap['required']}%."
                )

            })

    # =====================================================
    # GENERAL ACTIONS
    # =====================================================

    if score < 60:

        actions.append({

            "icon": "📚",

            "title": "Follow your learning path",

            "description": (
                "Complete the recommended learning "
                "steps to close your largest skill gaps."
            )

        })

    elif score < 75:

        actions.append({

            "icon": "🚀",

            "title": "Strengthen practical skills",

            "description": (
                "Build projects and practice the skills "
                "required for your target career."
            )

        })

    else:

        actions.append({

            "icon": "💼",

            "title": (
                "Start applying for suitable jobs"
            ),

            "description": (
                "Your profile is approaching or has "
                "reached a strong level of career readiness."
            )

        })

    # =====================================================
    # PROFILE ACTION
    # =====================================================

    actions.append({

        "icon": "👤",

        "title": "Keep your profile updated",

        "description": (
            "Maintain your education, skills, projects, "
            "certificates and experience information."
        )

    })

    return actions[:4]


# =========================================================
# READINESS DETAILS
# =========================================================

def get_readiness_details(
    student,
    career=None
):
    """
    Return complete readiness information for the UI.
    """

    if not student:

        return {

            "score": 0,

            "status": "Needs Improvement",

            "level": "Needs Improvement",

            "color": "needs-improvement",

            "career": career,

            "skill_breakdown": [],

            "strengths": [],

            "improvements": [],

            "actions": []

        }

    # =====================================================
    # SELECT CAREER
    # =====================================================

    selected_career = career

    if selected_career is None:

        selected_career = _get_best_career(
            student
        )

    # =====================================================
    # SCORE
    # =====================================================

    score = calculate_readiness(
        student,
        selected_career
    )

    # =====================================================
    # DETAILS
    # =====================================================

    skill_breakdown = get_skill_breakdown(
        student,
        selected_career
    )

    strengths = get_readiness_strengths(
        student,
        selected_career
    )

    improvements = get_readiness_improvements(
        student,
        selected_career
    )

    actions = get_recommended_actions(
        student,
        selected_career
    )

    return {

        "score": score,

        "status": get_readiness_status(
            score
        ),

        "level": get_readiness_level(
            score
        ),

        "color": get_readiness_color(
            score
        ),

        "career": selected_career,

        "skill_breakdown": skill_breakdown,

        "strengths": strengths,

        "improvements": improvements,

        "actions": actions

    }