# =========================================================
# SKILLBRIDGE AI
# ANALYTICS DATA SERVICE
# =========================================================

from services.career_recommender import (
    recommend_careers,
    get_career_profile
)

from services.skill_gap import (
    calculate_skill_gaps,
    get_skill_gap_summary
)

from services.readiness import (
    calculate_readiness,
    get_readiness_status
)


# =========================================================
# STUDENT SKILLS
# =========================================================

def get_student_skill_data(student):

    result = []

    if not student:
        return result

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

            result.append({
                "skill": skill.name,
                "proficiency": (
                    student_skill.proficiency or 0
                ),
                "category": (
                    getattr(
                        skill,
                        "category",
                        "Technical"
                    )
                )
            })

    return result


# =========================================================
# CAREER RECOMMENDATIONS
# =========================================================

def get_career_analytics(student):

    recommendations = recommend_careers(
        student
    )

    result = []

    for item in recommendations:

        if isinstance(item, dict):

            result.append({
                "career": item.get(
                    "career",
                    "Unknown"
                ),
                "match": item.get(
                    "match",
                    0
                ),
                "description": item.get(
                    "description",
                    ""
                )
            })

        else:

            result.append({
                "career": str(item),
                "match": 0,
                "description": ""
            })

    return result


# =========================================================
# TARGET CAREER
# =========================================================

def get_target_career(student):

    recommendations = get_career_analytics(
        student
    )

    if not recommendations:
        return None

    return recommendations[0]["career"]


# =========================================================
# SKILL GAP ANALYTICS
# =========================================================

def get_skill_gap_analytics(student):

    career = get_target_career(
        student
    )

    if not career:

        return {
            "career": None,
            "gaps": [],
            "summary": {}
        }

    gaps = calculate_skill_gaps(
        student,
        career
    )

    summary = get_skill_gap_summary(
        gaps
    )

    return {
        "career": career,
        "gaps": gaps,
        "summary": summary
    }


# =========================================================
# READINESS ANALYTICS
# =========================================================

def get_readiness_analytics(student):

    score = calculate_readiness(
        student
    )

    status = get_readiness_status(
        score
    )

    return {
        "score": score,
        "status": status
    }


# =========================================================
# COMPLETE POWER BI DATASET
# =========================================================

def build_analytics_dataset(student):

    skills = get_student_skill_data(
        student
    )

    careers = get_career_analytics(
        student
    )

    skill_gap = get_skill_gap_analytics(
        student
    )

    readiness = get_readiness_analytics(
        student
    )

    return {
        "student": {
            "id": student.id,
            "education": student.education,
            "degree": student.degree,
            "branch": student.branch,
            "college": student.college,
            "graduation_year": student.graduation_year,
            "experience_level": student.experience_level,
            "location": student.location
        },

        "skills": skills,

        "careers": careers,

        "skill_gap": skill_gap,

        "readiness": readiness
    }