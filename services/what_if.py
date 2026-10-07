# =========================================================
# SKILLBRIDGE AI
# WHAT-IF CAREER SIMULATION SERVICE
# =========================================================

from services.career_recommender import (
    CAREER_PROFILES,
    recommend_careers
)

from services.readiness import (
    calculate_readiness
)

from services.learning_progress import (
    get_student_learning_progress
)


# =========================================================
# HELPERS
# =========================================================

def _normalize_skill_name(skill_name):
    """
    Normalize skill names for reliable comparison.

    Examples:
        Power BI
        power bi
        POWER BI

    all become:
        power bi
    """

    if skill_name is None:
        return ""

    return " ".join(
        str(skill_name)
        .strip()
        .lower()
        .split()
    )


def _safe_number(value, default=0):
    """
    Safely convert a value to float.
    """

    try:
        return float(value)
    except (
        TypeError,
        ValueError
    ):
        return default


# =========================================================
# LEARNING EVIDENCE
# =========================================================

def _get_learning_evidence(student):
    """
    Read learning progress and convert it into effective
    skill proficiency.

    Example:

        Communication -> 100

    If multiple courses exist for the same skill,
    the highest progress value is used.
    """

    evidence = {}

    if student is None:
        return evidence

    try:

        progress_items = (
            get_student_learning_progress(
                student
            )
        )

    except Exception:

        progress_items = []

    for item in progress_items:

        skill_name = getattr(
            item,
            "skill",
            ""
        )

        normalized = _normalize_skill_name(
            skill_name
        )

        if not normalized:
            continue

        progress = _safe_number(
            getattr(
                item,
                "progress_percentage",
                0
            )
        )

        progress = max(
            0,
            min(
                100,
                progress
            )
        )

        previous = evidence.get(
            normalized,
            0
        )

        if progress > previous:

            evidence[
                normalized
            ] = progress

    return evidence


# =========================================================
# STUDENT SKILLS
# =========================================================

def _get_student_skill_dict(student):
    """
    Return the student's effective skills.

    Effective skill level is:

        MAX(
            StudentSkill proficiency,
            LearningProgress percentage
        )

    This prevents completed learning from being ignored.
    """

    skills = {}

    if student is None:
        return skills

    # -----------------------------------------------------
    # STUDENT SKILLS
    # -----------------------------------------------------

    student_skills = getattr(
        student,
        "student_skills",
        []
    )

    for student_skill in student_skills:

        skill = getattr(
            student_skill,
            "skill",
            None
        )

        if skill is None:
            continue

        skill_name = getattr(
            skill,
            "name",
            None
        )

        if not skill_name:
            continue

        proficiency = _safe_number(
            getattr(
                student_skill,
                "proficiency",
                0
            )
        )

        proficiency = max(
            0,
            min(
                100,
                proficiency
            )
        )

        normalized = _normalize_skill_name(
            skill_name
        )

        existing = skills.get(
            normalized,
            {
                "name": skill_name,
                "level": 0
            }
        )

        if proficiency > existing["level"]:

            existing["level"] = proficiency

        skills[
            normalized
        ] = existing

    # -----------------------------------------------------
    # LEARNING PROGRESS
    # -----------------------------------------------------

    learning_evidence = (
        _get_learning_evidence(
            student
        )
    )

    for normalized, progress in learning_evidence.items():

        if normalized in skills:

            if progress > skills[
                normalized
            ]["level"]:

                skills[
                    normalized
                ]["level"] = progress

        else:

            skills[
                normalized
            ] = {
                "name": normalized,
                "level": progress
            }

    # -----------------------------------------------------
    # RETURN SIMPLE DICTIONARY
    # -----------------------------------------------------

    return {
        item["name"]: int(
            round(
                item["level"]
            )
        )
        for item in skills.values()
    }


# =========================================================
# FIND STUDENT SKILL
# =========================================================

def _find_student_skill(
    student_skills,
    required_skill
):
    """
    Find a skill using normalized names.
    """

    required_normalized = (
        _normalize_skill_name(
            required_skill
        )
    )

    for skill_name, proficiency in (
        student_skills.items()
    ):

        if (
            _normalize_skill_name(
                skill_name
            )
            ==
            required_normalized
        ):

            return _safe_number(
                proficiency
            )

    return 0


# =========================================================
# CAREER MATCH CALCULATION
# =========================================================

def calculate_what_if_match(
    student_skills,
    required_skills
):
    """
    Calculate career match from 0 to 100.
    """

    if not required_skills:
        return 0

    total_score = 0
    total_skills = 0

    # -----------------------------------------------------
    # DICTIONARY REQUIREMENTS
    # -----------------------------------------------------

    if isinstance(
        required_skills,
        dict
    ):

        for skill_name, required_level in (
            required_skills.items()
        ):

            required_level = _safe_number(
                required_level
            )

            required_level = max(
                0,
                min(
                    100,
                    required_level
                )
            )

            if required_level <= 0:
                continue

            current_level = (
                _find_student_skill(
                    student_skills,
                    skill_name
                )
            )

            effective_level = min(
                current_level,
                required_level
            )

            score = (
                effective_level
                /
                required_level
            ) * 100

            total_score += score
            total_skills += 1

    # -----------------------------------------------------
    # LIST REQUIREMENTS
    # -----------------------------------------------------

    else:

        for skill_name in required_skills:

            current_level = (
                _find_student_skill(
                    student_skills,
                    skill_name
                )
            )

            total_score += current_level
            total_skills += 1

    if total_skills == 0:
        return 0

    return round(
        total_score / total_skills,
        2
    )


# =========================================================
# CAREER REQUIRED SKILLS
# =========================================================

def get_career_required_skills(
    career_name
):
    """
    Return required skills for a career.
    """

    profile = CAREER_PROFILES.get(
        career_name
    )

    if not profile:
        return {}

    return profile.get(
        "skills",
        {}
    ) or {}


# =========================================================
# SIMULATE CAREER
# =========================================================

def simulate_career(
    student,
    career_name,
    hypothetical_skills=None
):
    """
    Run a complete What-If career simulation.

    IMPORTANT:

    Hypothetical values are used only in memory.

    The student's actual database profile
    is never modified.
    """

    hypothetical_skills = (
        hypothetical_skills
        or {}
    )

    # -----------------------------------------------------
    # CURRENT EFFECTIVE SKILLS
    # -----------------------------------------------------

    current_skills = (
        _get_student_skill_dict(
            student
        )
    )

    # -----------------------------------------------------
    # COPY FOR SIMULATION
    # -----------------------------------------------------

    simulated_skills = dict(
        current_skills
    )

    # -----------------------------------------------------
    # APPLY HYPOTHETICAL VALUES
    # -----------------------------------------------------

    for skill_name, value in (
        hypothetical_skills.items()
    ):

        if not skill_name:
            continue

        value = _safe_number(
            value
        )

        value = max(
            0,
            min(
                100,
                value
            )
        )

        existing_name = None

        for existing_skill in (
            simulated_skills.keys()
        ):

            if (
                _normalize_skill_name(
                    existing_skill
                )
                ==
                _normalize_skill_name(
                    skill_name
                )
            ):

                existing_name = (
                    existing_skill
                )

                break

        if existing_name:

            simulated_skills[
                existing_name
            ] = int(
                round(value)
            )

        else:

            simulated_skills[
                skill_name
            ] = int(
                round(value)
            )

    # -----------------------------------------------------
    # REQUIRED SKILLS
    # -----------------------------------------------------

    required_skills = (
        get_career_required_skills(
            career_name
        )
    )

    # -----------------------------------------------------
    # CURRENT MATCH
    # -----------------------------------------------------

    current_match = (
        calculate_what_if_match(
            current_skills,
            required_skills
        )
    )

    # -----------------------------------------------------
    # SIMULATED MATCH
    # -----------------------------------------------------

    simulated_match = (
        calculate_what_if_match(
            simulated_skills,
            required_skills
        )
    )

    improvement = round(
        simulated_match
        -
        current_match,
        2
    )

    # =====================================================
    # SIMULATED SKILL GAPS
    # =====================================================

    gaps = []

    if isinstance(
        required_skills,
        dict
    ):

        for skill_name, required_level in (
            required_skills.items()
        ):

            required_level = int(
                round(
                    _safe_number(
                        required_level
                    )
                )
            )

            if required_level <= 0:
                continue

            current_level = int(
                round(
                    _find_student_skill(
                        simulated_skills,
                        skill_name
                    )
                )
            )

            gap = max(
                required_level
                -
                current_level,
                0
            )

            if gap <= 0:
                continue

            percentage = round(
                (
                    current_level
                    /
                    required_level
                ) * 100,
                2
            )

            # -------------------------------------------------
            # PRIORITY
            # -------------------------------------------------

            if gap >= 50:

                priority = "Critical"

            elif gap >= 30:

                priority = "High"

            elif gap >= 15:

                priority = "Medium"

            else:

                priority = "Low"

            gaps.append({

                "skill":
                    skill_name,

                "current":
                    current_level,

                "required":
                    required_level,

                "gap":
                    gap,

                "percentage":
                    percentage,

                "priority":
                    priority
            })

    else:

        for skill_name in required_skills:

            current_level = int(
                round(
                    _find_student_skill(
                        simulated_skills,
                        skill_name
                    )
                )
            )

            gap = max(
                100
                -
                current_level,
                0
            )

            if gap <= 0:
                continue

            if gap >= 50:

                priority = "Critical"

            elif gap >= 30:

                priority = "High"

            elif gap >= 15:

                priority = "Medium"

            else:

                priority = "Low"

            gaps.append({

                "skill":
                    skill_name,

                "current":
                    current_level,

                "required":
                    100,

                "gap":
                    gap,

                "percentage":
                    current_level,

                "priority":
                    priority
            })

    # -----------------------------------------------------
    # BIGGEST GAPS FIRST
    # -----------------------------------------------------

    gaps.sort(
        key=lambda item: (
            -item["gap"]
        )
    )

    # =====================================================
    # READINESS
    # =====================================================

    try:

        current_readiness = (
            calculate_readiness(
                student
            )
        )

    except Exception:

        current_readiness = 0

    current_readiness = _safe_number(
        current_readiness
    )

    # -----------------------------------------------------
    # SIMULATED READINESS
    # -----------------------------------------------------
    #
    # The What-If simulator estimates readiness
    # improvement from career-match improvement.
    #
    # This does NOT modify the actual readiness score.
    # -----------------------------------------------------

    readiness_improvement = round(
        max(
            0,
            improvement * 0.5
        ),
        2
    )

    simulated_readiness = round(
        min(
            100,
            current_readiness
            +
            readiness_improvement
        ),
        2
    )

    # =====================================================
    # IMPROVED SKILLS
    # =====================================================

    skills_improved = 0

    for skill_name, simulated_value in (
        simulated_skills.items()
    ):

        current_value = (
            _find_student_skill(
                current_skills,
                skill_name
            )
        )

        if (
            simulated_value
            >
            current_value
        ):

            skills_improved += 1

    # =====================================================
    # RESULT
    # =====================================================

    return {

        "career":
            career_name,

        "current_match":
            current_match,

        "simulated_match":
            simulated_match,

        "improvement":
            improvement,

        "current_readiness":
            current_readiness,

        "simulated_readiness":
            simulated_readiness,

        "readiness_improvement":
            readiness_improvement,

        "hypothetical_skills":
            hypothetical_skills,

        "current_skills":
            current_skills,

        "simulated_skills":
            simulated_skills,

        "required_skills":
            required_skills,

        "remaining_gaps":
            gaps,

        "gap_count":
            len(gaps),

        "skills_improved":
            skills_improved
    }


# =========================================================
# WHAT-IF OPTIONS
# =========================================================

def get_what_if_options(student):
    """
    Prepare career information for the What-If UI.
    """

    current_skills = (
        _get_student_skill_dict(
            student
        )
    )

    careers = []

    recommendations = (
        recommend_careers(
            student
        )
    )

    for recommendation in (
        recommendations
    ):

        if isinstance(
            recommendation,
            dict
        ):

            career_name = (
                recommendation.get(
                    "career",
                    ""
                )
            )

            current_match = (
                recommendation.get(
                    "match",
                    0
                )
            )

        else:

            career_name = str(
                recommendation
            )

            current_match = 0

        if not career_name:
            continue

        required_skills = (
            get_career_required_skills(
                career_name
            )
        )

        skill_rows = []

        if isinstance(
            required_skills,
            dict
        ):

            for skill_name, required_level in (
                required_skills.items()
            ):

                current_level = (
                    _find_student_skill(
                        current_skills,
                        skill_name
                    )
                )

                required_level = int(
                    round(
                        _safe_number(
                            required_level
                        )
                    )
                )

                skill_rows.append({

                    "skill":
                        skill_name,

                    "current":
                        int(
                            round(
                                current_level
                            )
                        ),

                    "required":
                        required_level
                })

        else:

            for skill_name in (
                required_skills
            ):

                current_level = (
                    _find_student_skill(
                        current_skills,
                        skill_name
                    )
                )

                skill_rows.append({

                    "skill":
                        skill_name,

                    "current":
                        int(
                            round(
                                current_level
                            )
                        ),

                    "required":
                        100
                })

        careers.append({

            "career":
                career_name,

            "current_match":
                current_match,

            "required_skills":
                skill_rows
        })

    return careers


# =========================================================
# SIMULATION SUMMARY
# =========================================================

def get_simulation_summary(
    simulation
):
    """
    Create summary messages for the UI.
    """

    if not simulation:
        return {
            "message":
                "No simulation data available.",

            "gap_message":
                "No skill-gap information available."
        }

    improvement = _safe_number(
        simulation.get(
            "improvement",
            0
        )
    )

    gap_count = int(
        _safe_number(
            simulation.get(
                "gap_count",
                0
            )
        )
    )

    if improvement > 0:

        message = (
            f"Your career match could "
            f"improve by {improvement:.2f}%."
        )

    elif improvement == 0:

        message = (
            "The selected skill changes did "
            "not increase the career match yet."
        )

    else:

        message = (
            "The simulated skill values "
            "reduced your career match."
        )

    if gap_count == 0:

        gap_message = (
            "Excellent! No skill gaps remain."
        )

    elif gap_count == 1:

        gap_message = (
            "Only 1 skill gap remains."
        )

    else:

        gap_message = (
            f"{gap_count} skill gaps remain."
        )

    return {

        "message":
            message,

        "gap_message":
            gap_message
    }


# =========================================================
# AVAILABLE CAREERS
# =========================================================

def get_available_careers():
    """
    Return all careers from CAREER_PROFILES.
    """

    return list(
        CAREER_PROFILES.keys()
    )


# =========================================================
# COMPARE SIMULATION
# =========================================================

def compare_simulation(
    current_simulation,
    simulated_result
):
    """
    Compare current and simulated states.
    """

    current_simulation = (
        current_simulation
        or {}
    )

    simulated_result = (
        simulated_result
        or {}
    )

    current_match = _safe_number(
        current_simulation.get(
            "current_match",
            current_simulation.get(
                "match",
                0
            )
        )
    )

    simulated_match = _safe_number(
        simulated_result.get(
            "simulated_match",
            simulated_result.get(
                "match",
                0
            )
        )
    )

    current_readiness = _safe_number(
        current_simulation.get(
            "current_readiness",
            current_simulation.get(
                "readiness",
                0
            )
        )
    )

    simulated_readiness = _safe_number(
        simulated_result.get(
            "simulated_readiness",
            simulated_result.get(
                "readiness",
                0
            )
        )
    )

    current_gaps = (
        current_simulation.get(
            "remaining_gaps",
            current_simulation.get(
                "gaps",
                []
            )
        )
        or []
    )

    simulated_gaps = (
        simulated_result.get(
            "remaining_gaps",
            simulated_result.get(
                "gaps",
                []
            )
        )
        or []
    )

    match_change = round(
        simulated_match
        -
        current_match,
        2
    )

    readiness_change = round(
        simulated_readiness
        -
        current_readiness,
        2
    )

    gap_change = (
        len(current_gaps)
        -
        len(simulated_gaps)
    )

    return {

        "current_match":
            current_match,

        "simulated_match":
            simulated_match,

        "match_change":
            match_change,

        "current_readiness":
            current_readiness,

        "simulated_readiness":
            simulated_readiness,

        "readiness_change":
            readiness_change,

        "current_gap_count":
            len(current_gaps),

        "simulated_gap_count":
            len(simulated_gaps),

        "gap_change":
            gap_change,

        "match_improved":
            match_change > 0,

        "readiness_improved":
            readiness_change > 0,

        "gaps_reduced":
            gap_change > 0
    }
# =========================================================
# NEXT LEARNING RECOMMENDATION
# =========================================================

def get_next_learning_recommendation(simulation):
    """
    Return the most important next learning recommendation
    based on the remaining skill gaps.
    """

    if not simulation:
        return {
            "available": False,
            "message": "Run a What-If career simulation first."
        }

    remaining_gaps = (
        simulation.get(
            "remaining_gaps",
            []
        )
        or []
    )

    if not remaining_gaps:
        return {
            "available": False,
            "message": (
                "Excellent! No major skill gaps remain "
                "for this career."
            )
        }

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    def gap_value(item):
        try:
            return float(
                item.get(
                    "gap",
                    0
                )
            )
        except (
            TypeError,
            ValueError
        ):
            return 0

    # -----------------------------------------------------
    # SORT BY PRIORITY + GAP
    # -----------------------------------------------------

    gaps = sorted(
        remaining_gaps,
        key=lambda item: (
            priority_order.get(
                item.get(
                    "priority",
                    "Low"
                ),
                5
            ),
            -gap_value(item)
        )
    )

    top_gap = gaps[0]

    skill = str(
        top_gap.get(
            "skill",
            "Unknown Skill"
        )
    ).strip()

    current = gap_value(
        top_gap.get(
            "current",
            0
        )
    )

    required = gap_value(
        top_gap.get(
            "required",
            0
        )
    )

    gap = gap_value(
        top_gap.get(
            "gap",
            0
        )
    )

    priority = top_gap.get(
        "priority",
        "Medium"
    )

    # -----------------------------------------------------
    # COURSE RECOMMENDATION
    # -----------------------------------------------------

    course_map = {

        "python":
            "Python for Data Science",

        "sql":
            "SQL & Data Analytics",

        "excel":
            "Advanced Excel for Data Analysis",

        "power bi":
            "Power BI Business Intelligence",

        "statistics":
            "Statistics for Data Analytics",

        "data visualization":
            "Data Visualization",

        "pandas":
            "Pandas for Data Analysis",

        "numpy":
            "NumPy for Data Science",

        "machine learning":
            "Machine Learning Fundamentals",

        "deep learning":
            "Deep Learning Fundamentals",

        "networking":
            "Computer Networking Fundamentals",

        "cybersecurity":
            "Cybersecurity Fundamentals",

        "linux":
            "Linux for Cybersecurity",

        "security tools":
            "Cybersecurity Tools",

        "cryptography":
            "Cryptography Fundamentals",

        "ethical hacking":
            "Ethical Hacking Fundamentals",

        "risk management":
            "Cybersecurity Risk Management",

        "git":
            "Git & GitHub",

        "html":
            "HTML Fundamentals",

        "css":
            "CSS Fundamentals",

        "javascript":
            "JavaScript Fundamentals",

        "flask":
            "Flask Web Development",

        "rest api":
            "REST API Development",

        "communication":
            "Professional Communication",

        "problem solving":
            "Problem Solving",

        "business analysis":
            "Business Analysis Fundamentals"
    }

    normalized_skill = _normalize_skill_name(
        skill
    )

    course = course_map.get(
        normalized_skill,
        f"{skill} Fundamentals"
    )

    # -----------------------------------------------------
    # ESTIMATED DURATION
    # -----------------------------------------------------

    if gap > 50:

        duration = "6-8 weeks"

    elif gap > 25:

        duration = "4-6 weeks"

    elif gap > 10:

        duration = "2-4 weeks"

    else:

        duration = "1-2 weeks"

    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    message = (
        f"Focus on {skill} next. "
        f"Your current level is "
        f"{int(round(current))}% "
        f"and the required level is "
        f"{int(round(required))}%."
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    return {

        "available":
            True,

        "skill":
            skill,

        "current":
            int(round(current)),

        "required":
            int(round(required)),

        "gap":
            int(round(gap)),

        "priority":
            priority,

        "course":
            course,

        "duration":
            duration,

        "message":
            message
    }