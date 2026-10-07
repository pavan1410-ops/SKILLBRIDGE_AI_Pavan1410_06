# =========================================================
# SKILLBRIDGE AI
# AI JOB MATCHING SERVICE
# =========================================================

from services.career_recommender import get_student_skills
from services.learning_progress import get_student_learning_progress


# =========================================================
# JOB DATABASE
# =========================================================

JOB_DATABASE = [

    {
        "title": "Data Analyst",
        "company": "Microsoft",
        "location": "India / Remote",
        "description": (
            "Analyze business data and create insights "
            "using analytics and visualization tools."
        ),
        "required_skills": {
            "Python": 80,
            "SQL": 80,
            "Excel": 75,
            "Power BI": 75,
            "Statistics": 70,
            "Data Visualization": 70
        },
        "apply_url": "https://careers.microsoft.com/"
    },

    {
        "title": "Data Analyst",
        "company": "Amazon",
        "location": "India / Remote",
        "description": (
            "Work with large datasets to generate "
            "business insights and analytical reports."
        ),
        "required_skills": {
            "Python": 75,
            "SQL": 85,
            "Excel": 80,
            "Statistics": 70,
            "Data Visualization": 70
        },
        "apply_url": "https://www.amazon.jobs/"
    },

    {
        "title": "Business Analyst",
        "company": "Deloitte",
        "location": "India",
        "description": (
            "Analyze business requirements, data and "
            "processes to support organizational decisions."
        ),
        "required_skills": {
            "Excel": 80,
            "SQL": 65,
            "Power BI": 70,
            "Statistics": 60,
            "Business Analysis": 80,
            "Communication": 75
        },
        "apply_url": "https://jobs.deloitte.com/"
    },

    {
        "title": "Data Scientist",
        "company": "IBM",
        "location": "India / Remote",
        "description": (
            "Develop analytical and machine-learning "
            "solutions using data."
        ),
        "required_skills": {
            "Python": 85,
            "SQL": 75,
            "Statistics": 80,
            "Pandas": 80,
            "NumPy": 75,
            "Machine Learning": 80
        },
        "apply_url": "https://www.ibm.com/careers"
    },

    {
        "title": "Cybersecurity Analyst",
        "company": "Cisco",
        "location": "India",
        "description": (
            "Monitor security events, investigate threats "
            "and support cybersecurity operations."
        ),
        "required_skills": {
            "Networking": 80,
            "Linux": 70,
            "Cybersecurity": 80,
            "Security Tools": 75,
            "Risk Management": 65
        },
        "apply_url": "https://jobs.cisco.com/"
    }
]


# =========================================================
# NORMALIZE SKILL NAME
# =========================================================

def _normalize_skill_name(skill):
    """
    Normalize skill names for reliable matching.

    Example:

        "Communication"
        "communication"
        " COMMUNICATION "

    become:

        "communication"
    """

    return " ".join(
        str(skill or "")
        .strip()
        .lower()
        .split()
    )


# =========================================================
# SAFE INTEGER
# =========================================================

def _safe_int(value, default=0):

    try:
        return int(float(value))

    except (TypeError, ValueError):
        return default


# =========================================================
# GET LEARNING EVIDENCE
# =========================================================

def get_learning_evidence(student):
    """
    Get the highest learning-progress percentage
    for each skill.

    Example:

        Communication -> 100
        Python -> 80
        SQL -> 60
    """

    evidence = {}

    if not student:
        return evidence

    try:
        progress_items = (
            get_student_learning_progress(student)
        )

    except Exception:
        progress_items = []

    if not progress_items:
        return evidence

    for item in progress_items:

        skill = _normalize_skill_name(
            getattr(item, "skill", "")
        )

        if not skill:
            continue

        progress = _safe_int(
            getattr(
                item,
                "progress_percentage",
                0
            )
        )

        progress = max(
            0,
            min(100, progress)
        )

        existing = evidence.get(
            skill,
            0
        )

        # If multiple courses exist for the same skill,
        # use the highest progress as evidence.
        if progress > existing:

            evidence[skill] = progress

    return evidence


# =========================================================
# GET EFFECTIVE STUDENT SKILLS
# =========================================================

def get_effective_student_skills(student):
    """
    Combine:

        1. Student Skill Proficiency
        2. Learning Progress Evidence

    The higher value becomes the effective skill level.

    Example:

        StudentSkill:
            Communication = 0

        LearningProgress:
            Communication = 100

        Effective:
            Communication = 100
    """

    try:

        raw_skills = get_student_skills(
            student
        )

    except Exception:

        raw_skills = {}

    if raw_skills is None:
        raw_skills = {}

    effective_skills = {}

    # =====================================================
    # 1. STUDENT PROFILE SKILLS
    # =====================================================

    for skill, proficiency in raw_skills.items():

        normalized_skill = _normalize_skill_name(
            skill
        )

        if not normalized_skill:
            continue

        proficiency = _safe_int(
            proficiency
        )

        proficiency = max(
            0,
            min(100, proficiency)
        )

        existing = effective_skills.get(
            normalized_skill,
            0
        )

        effective_skills[normalized_skill] = max(
            existing,
            proficiency
        )

    # =====================================================
    # 2. LEARNING PROGRESS
    # =====================================================

    learning_evidence = get_learning_evidence(
        student
    )

    # =====================================================
    # 3. MERGE BOTH SOURCES
    # =====================================================

    for skill, progress in learning_evidence.items():

        current = effective_skills.get(
            skill,
            0
        )

        effective_skills[skill] = max(
            current,
            progress
        )

    return effective_skills


# =========================================================
# GET STUDENT SKILLS
# =========================================================

def get_student_skill_dict(student):
    """
    Backward-compatible function.

    Returns effective student skills including
    learning-progress evidence.
    """

    return get_effective_student_skills(
        student
    )


# =========================================================
# CALCULATE JOB MATCH
# =========================================================

def calculate_job_match(
    student_skills,
    required_skills
):
    """
    Calculate job match percentage.

    Each required skill contributes according to
    the student's current proficiency.

    A skill cannot contribute more than 100%.
    """

    if not required_skills:
        return 0

    normalized_student = {}

    for skill, value in student_skills.items():

        normalized_skill = _normalize_skill_name(
            skill
        )

        if not normalized_skill:
            continue

        value = _safe_int(
            value
        )

        value = max(
            0,
            min(100, value)
        )

        normalized_student[normalized_skill] = (
            max(
                normalized_student.get(
                    normalized_skill,
                    0
                ),
                value
            )
        )

    total = 0
    count = 0

    for skill, required_level in (
        required_skills.items()
    ):

        required_level = _safe_int(
            required_level
        )

        if required_level <= 0:
            continue

        current_level = normalized_student.get(
            _normalize_skill_name(skill),
            0
        )

        match = min(
            current_level /
            required_level,
            1
        )

        total += match
        count += 1

    if count == 0:
        return 0

    return round(
        (total / count) * 100,
        2
    )


# =========================================================
# GET JOB SKILL DETAILS
# =========================================================

def get_job_skill_details(
    student_skills,
    required_skills
):
    """
    Explain exactly why a student matches a job.
    """

    normalized_student = {}

    for skill, value in student_skills.items():

        normalized_skill = _normalize_skill_name(
            skill
        )

        if not normalized_skill:
            continue

        value = _safe_int(
            value
        )

        value = max(
            0,
            min(100, value)
        )

        normalized_student[normalized_skill] = max(
            normalized_student.get(
                normalized_skill,
                0
            ),
            value
        )

    details = []

    for skill, required_level in (
        required_skills.items()
    ):

        required_level = _safe_int(
            required_level
        )

        if required_level <= 0:
            continue

        current_level = normalized_student.get(
            _normalize_skill_name(skill),
            0
        )

        gap = max(
            required_level - current_level,
            0
        )

        percentage = (
            min(
                current_level /
                required_level,
                1
            ) * 100
        )

        if current_level >= required_level:

            status = "Strong"

        elif percentage >= 75:

            status = "Good"

        elif percentage >= 50:

            status = "Developing"

        else:

            status = "Needs Improvement"

        details.append({

            "skill": skill,

            "current": current_level,

            "required": required_level,

            "gap": gap,

            "percentage": round(
                percentage,
                2
            ),

            "status": status

        })

    return details


# =========================================================
# MATCH JOBS
# =========================================================

def match_job(student):
    """
    Match the student against all available jobs.

    Learning progress is included as skill evidence.

    Returns jobs sorted from highest match
    to lowest match.
    """

    student_skills = get_effective_student_skills(
        student
    )

    results = []

    for job in JOB_DATABASE:

        required_skills = job.get(
            "required_skills",
            {}
        )

        match_percentage = calculate_job_match(
            student_skills,
            required_skills
        )

        skill_details = get_job_skill_details(
            student_skills,
            required_skills
        )

        matching_skills = [
            item
            for item in skill_details
            if item["current"] >= item["required"]
        ]

        missing_skills = [
            item
            for item in skill_details
            if item["gap"] > 0
        ]

        results.append({

            "title": job.get(
                "title",
                ""
            ),

            "company": job.get(
                "company",
                ""
            ),

            "location": job.get(
                "location",
                ""
            ),

            "description": job.get(
                "description",
                ""
            ),

            "required_skills": required_skills,

            "skill_details": skill_details,

            "matching_skills": matching_skills,

            "missing_skills": missing_skills,

            "match_percentage": match_percentage,

            "apply_url": job.get(
                "apply_url",
                "#"
            )

        })

    results.sort(
        key=lambda job: job[
            "match_percentage"
        ],
        reverse=True
    )

    return results


# =========================================================
# COMPATIBILITY ALIAS
# =========================================================

def match_jobs(student):
    """
    Backward-compatible alias.

    Some older routes may still use match_jobs().
    """

    return match_job(student)