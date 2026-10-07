# =========================================================
# SKILLBRIDGE AI
# POWER BI EXPORT SERVICE
# =========================================================

from services.career_recommender import recommend_careers
from services.skill_gap import calculate_skill_gaps
from services.readiness import (
    calculate_readiness,
    get_readiness_status
)


# =========================================================
# 1. STUDENT ANALYTICS
# =========================================================

def get_student_analytics(student):

    return [{
        "StudentID": student.id,
        "UserID": student.user_id,
        "Education": student.education or "",
        "Degree": student.degree or "",
        "Branch": student.branch or "",
        "College": student.college or "",
        "GraduationYear": (
            student.graduation_year
            if student.graduation_year
            else ""
        ),
        "ExperienceLevel": (
            student.experience_level or ""
        ),
        "Location": student.location or ""
    }]


# =========================================================
# 2. SKILL ANALYTICS
# =========================================================

def get_skill_analytics(student):

    rows = []

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

        if skill:

            rows.append({

                "StudentID":
                    student.id,

                "SkillID":
                    skill.id,

                "Skill":
                    skill.name,

                "Category":
                    (
                        skill.category
                        if getattr(
                            skill,
                            "category",
                            None
                        )
                        else "Technical"
                    ),

                "Proficiency":
                    student_skill.proficiency or 0
            })

    return rows


# =========================================================
# 3. CAREER ANALYTICS
# =========================================================

def get_career_analytics(student):

    rows = []

    recommendations = recommend_careers(
        student
    )

    for item in recommendations:

        if isinstance(item, dict):

            rows.append({

                "StudentID":
                    student.id,

                "Career":
                    item.get(
                        "career",
                        ""
                    ),

                "MatchPercentage":
                    item.get(
                        "match",
                        0
                    ),

                "Description":
                    item.get(
                        "description",
                        ""
                    )
            })

        else:

            rows.append({

                "StudentID":
                    student.id,

                "Career":
                    str(item),

                "MatchPercentage":
                    0,

                "Description":
                    ""
            })

    return rows


# =========================================================
# 4. SKILL GAP ANALYTICS
# =========================================================

def get_skill_gap_analytics(student):

    rows = []

    recommendations = recommend_careers(
        student
    )

    if not recommendations:
        return rows

    first = recommendations[0]

    if isinstance(first, dict):

        career = first.get(
            "career",
            ""
        )

    else:

        career = str(first)

    if not career:
        return rows

    gaps = calculate_skill_gaps(
        student,
        career
    )

    for item in gaps:

        rows.append({

            "StudentID":
                student.id,

            "TargetCareer":
                career,

            "Skill":
                item.get(
                    "skill",
                    ""
                ),

            "CurrentLevel":
                item.get(
                    "current",
                    0
                ),

            "RequiredLevel":
                item.get(
                    "required",
                    0
                ),

            "Gap":
                item.get(
                    "gap",
                    0
                ),

            "Percentage":
                item.get(
                    "percentage",
                    0
                ),

            "Status":
                item.get(
                    "status",
                    ""
                ),

            "Priority":
                item.get(
                    "priority",
                    ""
                )
        })

    return rows


# =========================================================
# 5. READINESS ANALYTICS
# =========================================================

def get_readiness_analytics(student):

    score = calculate_readiness(
        student
    )

    status = get_readiness_status(
        score
    )

    return [{

        "StudentID":
            student.id,

        "ReadinessScore":
            score,

        "ReadinessStatus":
            status
    }]


# =========================================================
# COMPLETE POWER BI DATA
# ONE STUDENT
# =========================================================

def generate_powerbi_tables(student):

    return {

        "StudentAnalytics":
            get_student_analytics(
                student
            ),

        "SkillAnalytics":
            get_skill_analytics(
                student
            ),

        "CareerAnalytics":
            get_career_analytics(
                student
            ),

        "SkillGapAnalytics":
            get_skill_gap_analytics(
                student
            ),

        "ReadinessAnalytics":
            get_readiness_analytics(
                student
            )
    }