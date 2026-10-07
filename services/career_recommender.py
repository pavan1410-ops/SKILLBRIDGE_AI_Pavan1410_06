
# =========================================================
# SKILLBRIDGE AI
# CAREER RECOMMENDER SERVICE
# =========================================================

from models.student_skill import StudentSkill


# =========================================================
# CAREER PROFILES
# =========================================================
#
# Each career contains the important skills required for
# that career.
#
# proficiency = expected proficiency level (0-100)
#
# =========================================================

CAREER_PROFILES = {

    "Data Analyst": {
        "description": "Analyze data and create insights for business decisions.",
        "skills": {
            "Python": 80,
            "SQL": 85,
            "Excel": 80,
            "Power BI": 75,
            "Statistics": 75,
            "Data Visualization": 75,
            "Pandas": 70,
            "Communication": 70
        }
    },

    "Data Scientist": {
        "description": "Build statistical and machine-learning solutions from data.",
        "skills": {
            "Python": 90,
            "SQL": 75,
            "Statistics": 90,
            "Machine Learning": 90,
            "Pandas": 85,
            "NumPy": 80,
            "Data Visualization": 75,
            "Deep Learning": 70
        }
    },

    "Business Analyst": {
        "description": "Bridge business requirements and technical solutions.",
        "skills": {
            "Excel": 85,
            "SQL": 75,
            "Power BI": 75,
            "Business Analysis": 90,
            "Communication": 90,
            "Problem Solving": 85,
            "Data Visualization": 70
        }
    },

    "Cybersecurity Analyst": {
        "description": "Protect systems, networks and data from security threats.",
        "skills": {
            "Networking": 85,
            "Cybersecurity": 90,
            "Linux": 75,
            "Python": 70,
            "Security Tools": 80,
            "Cryptography": 70,
            "Ethical Hacking": 80,
            "Risk Management": 75
        }
    },

    "Machine Learning Engineer": {
        "description": "Develop, deploy and maintain machine-learning systems.",
        "skills": {
            "Python": 90,
            "Machine Learning": 95,
            "Statistics": 85,
            "NumPy": 85,
            "Pandas": 85,
            "Deep Learning": 85,
            "SQL": 70,
            "Git": 75
        }
    },

    "Web Developer": {
        "description": "Build modern web applications and websites.",
        "skills": {
            "HTML": 85,
            "CSS": 80,
            "JavaScript": 85,
            "Python": 70,
            "Flask": 75,
            "SQL": 70,
            "Git": 75,
            "REST API": 75
        }
    }
}


# =========================================================
# GET STUDENT SKILLS
# =========================================================

def get_student_skills(student):
    """
    Convert the student's database skills into a dictionary.

    Example:

    {
        "Python": 80,
        "SQL": 70,
        "Excel": 90
    }
    """

    student_skills = StudentSkill.query.filter_by(
        student_id=student.id
    ).all()

    skills = {}

    for student_skill in student_skills:

        if student_skill.skill is None:
            continue

        skill_name = student_skill.skill.name

        skills[skill_name] = (
            student_skill.proficiency or 0
        )

    return skills


# =========================================================
# CALCULATE CAREER MATCH
# =========================================================

def calculate_career_match(
    student_skills,
    required_skills
):
    """
    Calculate how well the student's skills match
    the required career skills.

    Returns a percentage between 0 and 100.
    """

    if not required_skills:
        return 0

    total_score = 0

    for skill_name, required_level in required_skills.items():

        student_level = student_skills.get(
            skill_name,
            0
        )

        # Do not allow a skill to contribute more than
        # the required level.

        matched_level = min(
            student_level,
            required_level
        )

        if required_level > 0:

            skill_score = (
                matched_level / required_level
            ) * 100

        else:

            skill_score = 0

        total_score += skill_score

    score = (
        total_score / len(required_skills)
    )

    return round(
        min(100, max(0, score)),
        2
    )


# =========================================================
# RECOMMEND CAREERS
# =========================================================

def recommend_careers(student):
    """
    Generate career recommendations for a student.

    Returns a list such as:

    [
        {
            "career": "Data Analyst",
            "match": 88.5,
            "score": 88.5,
            "description": "..."
        }
    ]
    """

    student_skills = get_student_skills(
        student
    )

    recommendations = []

    for career_name, career_data in CAREER_PROFILES.items():

        required_skills = career_data.get(
            "skills",
            {}
        )

        match_score = calculate_career_match(
            student_skills,
            required_skills
        )

        recommendations.append({

            "career": career_name,

            "match": match_score,

            "score": match_score,

            "description": career_data.get(
                "description",
                ""
            )
        })

    # Highest match first

    recommendations.sort(
        key=lambda item: item["match"],
        reverse=True
    )

    return recommendations


# =========================================================
# GET CAREER PROFILE
# =========================================================

def get_career_profile(career):
    """
    Return a career profile by name.
    """

    return CAREER_PROFILES.get(
        career
    )
