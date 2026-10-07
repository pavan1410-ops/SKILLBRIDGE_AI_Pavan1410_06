# =========================================================
# SKILLBRIDGE AI
# AI CAREER DIGITAL TWIN SERVICE
# =========================================================

from services.career_recommender import recommend_careers
from services.skill_gap import calculate_skill_gaps
from services.learning_path import (
    generate_learning_path,
    create_complete_roadmap
)
from services.readiness import (
    calculate_readiness,
    get_readiness_status
)
from services.learning_progress import (
    get_student_learning_progress,
    get_learning_summary
)


# =========================================================
# NORMALIZE SKILL NAME
# =========================================================

def _normalize_skill_name(skill):
    """
    Normalize skill names so that:

        Python
        python
        PYTHON
        Python

    are treated as the same skill.
    """

    if skill is None:
        return ""

    return " ".join(
        str(skill).strip().lower().split()
    )


# =========================================================
# SAFE NUMBER
# =========================================================

def _safe_number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# =========================================================
# SAFE DICTIONARY VALUE
# =========================================================

def _get_value(item, key, default=None):

    if isinstance(item, dict):
        return item.get(key, default)

    return default


# =========================================================
# BUILD LEARNING EVIDENCE
# =========================================================

def _build_learning_evidence(learning_progress):
    """
    Build the highest learning-progress percentage
    for each skill.

    Example:

        Communication -> 100
        Python -> 60
        SQL -> 30
    """

    evidence = {}

    for progress in learning_progress:

        skill = _normalize_skill_name(
            getattr(progress, "skill", "")
        )

        if not skill:
            continue

        percentage = _safe_number(
            getattr(
                progress,
                "progress_percentage",
                0
            )
        )

        percentage = max(
            0,
            min(
                100,
                percentage
            )
        )

        current = evidence.get(
            skill,
            0
        )

        if percentage > current:
            evidence[skill] = percentage

    return evidence


# =========================================================
# BUILD EFFECTIVE SKILL EVIDENCE
# =========================================================

def _build_effective_skills(student, learning_evidence):
    """
    Combine:

        StudentSkill proficiency
                +
        LearningProgress evidence

    using the maximum value.

    Example:

        StudentSkill Communication = 0
        Course progress = 100

        Effective Communication = 100
    """

    effective_skills = {}

    # -----------------------------------------------------
    # StudentSkill proficiency
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

        if not skill:
            continue

        skill_name = getattr(
            skill,
            "name",
            ""
        )

        normalized = _normalize_skill_name(
            skill_name
        )

        if not normalized:
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

        effective_skills[normalized] = max(
            effective_skills.get(
                normalized,
                0
            ),
            proficiency
        )

    # -----------------------------------------------------
    # Learning evidence
    # -----------------------------------------------------

    for skill, progress in learning_evidence.items():

        effective_skills[skill] = max(
            effective_skills.get(
                skill,
                0
            ),
            progress
        )

    return effective_skills


# =========================================================
# BUILD EFFECTIVE SKILL DETAILS
# =========================================================

def _build_effective_skill_details(
    student,
    learning_progress
):
    """
    Create detailed evidence for every skill.

    Returns information such as:

        Profile Skill: 0
        Learning Evidence: 100
        Effective Skill: 100
    """

    learning_evidence = _build_learning_evidence(
        learning_progress
    )

    effective_skills = _build_effective_skills(
        student,
        learning_evidence
    )

    details = {}

    # -----------------------------------------------------
    # Add StudentSkill records
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

        if not skill:
            continue

        skill_name = getattr(
            skill,
            "name",
            ""
        )

        normalized = _normalize_skill_name(
            skill_name
        )

        if not normalized:
            continue

        profile_level = _safe_number(
            getattr(
                student_skill,
                "proficiency",
                0
            )
        )

        learning_level = learning_evidence.get(
            normalized,
            0
        )

        effective_level = effective_skills.get(
            normalized,
            0
        )

        details[normalized] = {
            "skill": skill_name,
            "profile_skill": int(
                round(profile_level)
            ),
            "learning_evidence": int(
                round(learning_level)
            ),
            "effective_skill": int(
                round(effective_level)
            )
        }

    # -----------------------------------------------------
    # Add skills that exist only through learning
    # -----------------------------------------------------

    for normalized, learning_level in learning_evidence.items():

        if normalized in details:
            continue

        details[normalized] = {
            "skill": normalized.title(),
            "profile_skill": 0,
            "learning_evidence": int(
                round(learning_level)
            ),
            "effective_skill": int(
                round(
                    effective_skills.get(
                        normalized,
                        learning_level
                    )
                )
            )
        }

    return list(
        details.values()
    )


# =========================================================
# BUILD AI CAREER DIGITAL TWIN
# =========================================================

def build_digital_twin(student):
    """
    Build the complete AI Career Digital Twin.

    Main flow:

        Student Profile
              ↓
        Student Skills
              ↓
        Learning Evidence
              ↓
        Effective Skills
              ↓
        Career Recommendation
              ↓
        Target Career
              ↓
        Skill Gap
              ↓
        Learning Path
              ↓
        Career Readiness
    """

    # =====================================================
    # 1. CAREER RECOMMENDATIONS
    # =====================================================

    recommendations = recommend_careers(
        student
    )

    if recommendations is None:
        recommendations = []

    if not isinstance(
        recommendations,
        list
    ):
        recommendations = list(
            recommendations
        )

    # =====================================================
    # 2. TARGET CAREER
    # =====================================================

    target_career = None

    if recommendations:

        first_recommendation = (
            recommendations[0]
        )

        if isinstance(
            first_recommendation,
            dict
        ):

            target_career = (
                first_recommendation.get(
                    "career"
                )
            )

        elif isinstance(
            first_recommendation,
            str
        ):

            target_career = (
                first_recommendation
            )

    # =====================================================
    # 3. LEARNING PROGRESS
    # =====================================================

    learning_progress = (
        get_student_learning_progress(
            student
        )
    )

    if learning_progress is None:
        learning_progress = []

    learning_summary = (
        get_learning_summary(
            student
        )
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
    # 4. LEARNING EVIDENCE
    # =====================================================

    learning_evidence = (
        _build_learning_evidence(
            learning_progress
        )
    )

    # =====================================================
    # 5. EFFECTIVE SKILLS
    # =====================================================

    effective_skills = (
        _build_effective_skills(
            student,
            learning_evidence
        )
    )

    effective_skill_details = (
        _build_effective_skill_details(
            student,
            learning_progress
        )
    )

    # =====================================================
    # 6. SKILL GAP
    # =====================================================

    skill_gaps = []

    skill_gap_summary = {
        "total_skills": 0,
        "strong_skills": 0,
        "skills_to_improve": 0,
        "critical_gaps": 0,
        "average_gap": 0,
        "completion": 0
    }

    if target_career:

        skill_gaps = calculate_skill_gaps(
            student,
            target_career
        )

        if skill_gaps is None:
            skill_gaps = []

        total_skills = len(
            skill_gaps
        )

        strong_skills = 0
        skills_to_improve = 0
        critical_gaps = 0
        total_gap = 0

        for item in skill_gaps:

            gap = _safe_number(
                _get_value(
                    item,
                    "gap",
                    0
                )
            )

            total_gap += gap

            if gap <= 0:

                strong_skills += 1

            else:

                skills_to_improve += 1

            priority = str(
                _get_value(
                    item,
                    "priority",
                    ""
                )
            ).strip().lower()

            if priority == "critical":

                critical_gaps += 1

            elif gap >= 40:

                critical_gaps += 1

        if total_skills > 0:

            average_gap = round(
                total_gap /
                total_skills,
                2
            )

            completion = round(
                (
                    strong_skills /
                    total_skills
                ) * 100,
                2
            )

        else:

            average_gap = 0
            completion = 100

        skill_gap_summary = {

            "total_skills": total_skills,

            "strong_skills": strong_skills,

            "skills_to_improve":
                skills_to_improve,

            "critical_gaps":
                critical_gaps,

            "average_gap":
                average_gap,

            "completion":
                completion
        }

    # =====================================================
    # 7. PERSONALIZED LEARNING PATH
    # =====================================================

    learning_path = []

    if target_career:

        learning_path = generate_learning_path(
            student,
            target_career
        )

        if learning_path is None:
            learning_path = []

    # =====================================================
    # 8. CONNECT LEARNING PROGRESS
    # =====================================================

    progress_lookup = {}

    for progress in learning_progress:

        skill = _normalize_skill_name(
            getattr(
                progress,
                "skill",
                ""
            )
        )

        course = _normalize_skill_name(
            getattr(
                progress,
                "course_name",
                ""
            )
        )

        key = (
            skill,
            course
        )

        progress_lookup[key] = progress

    for item in learning_path:

        if not isinstance(
            item,
            dict
        ):
            continue

        skill = _normalize_skill_name(
            item.get(
                "skill",
                ""
            )
        )

        course = _normalize_skill_name(
            item.get(
                "course",
                item.get(
                    "course_name",
                    ""
                )
            )
        )

        key = (
            skill,
            course
        )

        progress = progress_lookup.get(
            key
        )

        if progress:

            item["learning_status"] = (
                progress.status
            )

            item["progress_percentage"] = (
                progress.progress_percentage
            )

        else:

            item["learning_status"] = (
                "Not Started"
            )

            item["progress_percentage"] = 0

    # =====================================================
    # 9. COMPLETED LEARNING
    # =====================================================

    completed_learning = []

    in_progress_learning = []

    for progress in learning_progress:

        progress_item = {

            "id": progress.id,

            "skill": progress.skill,

            "course_name":
                progress.course_name,

            "status":
                progress.status,

            "progress_percentage":
                progress.progress_percentage,

            "started_at":
                progress.started_at,

            "completed_at":
                progress.completed_at,

            "created_at":
                progress.created_at
        }

        if progress.status == "Completed":

            completed_learning.append(
                progress_item
            )

        elif progress.status == "In Progress":

            in_progress_learning.append(
                progress_item
            )

    # =====================================================
    # 10. CAREER ROADMAP
    # =====================================================

    roadmap = []

    if target_career:

        roadmap = create_complete_roadmap(
            student,
            target_career
        )

        if roadmap is None:
            roadmap = []

    # =====================================================
    # 11. CAREER READINESS
    # =====================================================

    if target_career:

        readiness_score = calculate_readiness(
            student,
            target_career
        )

    else:

        readiness_score = 0

    readiness_score = _safe_number(
        readiness_score
    )

    readiness_score = round(
        readiness_score,
        2
    )

    readiness_score = max(
        0,
        min(
            100,
            readiness_score
        )
    )

    readiness_status = get_readiness_status(
        readiness_score
    )

    # =====================================================
    # 12. FINAL DIGITAL TWIN
    # =====================================================

    digital_twin = {

        "student_id":
            student.id,

        "target_career":
            target_career,

        "career_recommendations":
            recommendations,

        "readiness_score":
            readiness_score,

        "readiness_status":
            readiness_status,

        # -----------------------------------------------
        # SKILL GAP
        # -----------------------------------------------

        "skill_gaps":
            skill_gaps,

        "skill_gap_summary":
            skill_gap_summary,

        # -----------------------------------------------
        # EFFECTIVE SKILLS
        # -----------------------------------------------

        "learning_evidence":
            learning_evidence,

        "effective_skills":
            effective_skills,

        "effective_skill_details":
            effective_skill_details,

        # -----------------------------------------------
        # LEARNING
        # -----------------------------------------------

        "learning_path":
            learning_path,

        "roadmap":
            roadmap,

        "learning_progress":
            learning_progress,

        "learning_summary":
            learning_summary,

        "completed_learning":
            completed_learning,

        "in_progress_learning":
            in_progress_learning
    }

    return digital_twin