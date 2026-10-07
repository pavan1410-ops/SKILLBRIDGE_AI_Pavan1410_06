# =========================================================
# SKILLBRIDGE AI
# PERSONALIZED LEARNING PATH SERVICE
# =========================================================

from services.skill_gap import calculate_skill_gaps
from services.learning_progress import get_student_learning_progress


# =========================================================
# LEARNING RESOURCES
# =========================================================

LEARNING_RESOURCES = {

    "Python": {
        "course": "Python for Data Science",
        "topics": [
            "Python Fundamentals",
            "Functions and Modules",
            "Object-Oriented Programming",
            "File Handling",
            "Python for Data Analysis"
        ]
    },

    "SQL": {
        "course": "SQL & Database Analytics",
        "topics": [
            "SQL Fundamentals",
            "SELECT and WHERE",
            "JOINs",
            "GROUP BY and HAVING",
            "Subqueries",
            "Window Functions"
        ]
    },

    "Excel": {
        "course": "Advanced Excel for Analytics",
        "topics": [
            "Excel Fundamentals",
            "Formulas and Functions",
            "Pivot Tables",
            "Charts",
            "Lookup Functions",
            "Data Cleaning"
        ]
    },

    "Power BI": {
        "course": "Power BI Data Analytics",
        "topics": [
            "Power BI Fundamentals",
            "Power Query",
            "Data Modeling",
            "DAX",
            "Interactive Dashboards",
            "Power BI Reports"
        ]
    },

    "Statistics": {
        "course": "Statistics for Data Science",
        "topics": [
            "Descriptive Statistics",
            "Probability",
            "Distributions",
            "Hypothesis Testing",
            "Correlation",
            "Regression"
        ]
    },

    "Data Visualization": {
        "course": "Data Visualization",
        "topics": [
            "Visualization Principles",
            "Charts and Graphs",
            "Matplotlib",
            "Seaborn",
            "Dashboard Design"
        ]
    },

    "Pandas": {
        "course": "Pandas for Data Analysis",
        "topics": [
            "Series and DataFrames",
            "Data Cleaning",
            "Filtering",
            "Grouping",
            "Merging Data",
            "Data Transformation"
        ]
    },

    "NumPy": {
        "course": "NumPy Fundamentals",
        "topics": [
            "NumPy Arrays",
            "Array Operations",
            "Indexing",
            "Broadcasting",
            "Mathematical Operations"
        ]
    },

    "Machine Learning": {
        "course": "Machine Learning Fundamentals",
        "topics": [
            "Machine Learning Basics",
            "Regression",
            "Classification",
            "Clustering",
            "Model Evaluation",
            "Feature Engineering"
        ]
    },

    "Deep Learning": {
        "course": "Deep Learning",
        "topics": [
            "Neural Networks",
            "TensorFlow",
            "Keras",
            "CNN",
            "RNN",
            "Model Training"
        ]
    },

    "Networking": {
        "course": "Computer Networking",
        "topics": [
            "Networking Fundamentals",
            "TCP/IP",
            "DNS",
            "HTTP/HTTPS",
            "Network Security",
            "Firewalls"
        ]
    },

    "Cybersecurity": {
        "course": "Cybersecurity Fundamentals",
        "topics": [
            "Security Fundamentals",
            "Threats and Vulnerabilities",
            "Network Security",
            "Authentication",
            "Security Monitoring"
        ]
    },

    "Linux": {
        "course": "Linux Fundamentals",
        "topics": [
            "Linux Commands",
            "File System",
            "Permissions",
            "Processes",
            "Shell Scripting"
        ]
    },

    "Security Tools": {
        "course": "Cybersecurity Tools",
        "topics": [
            "Wireshark",
            "Nmap",
            "Burp Suite",
            "Security Monitoring"
        ]
    },

    "Cryptography": {
        "course": "Cryptography Fundamentals",
        "topics": [
            "Encryption",
            "Hashing",
            "Symmetric Cryptography",
            "Asymmetric Cryptography",
            "Digital Signatures"
        ]
    },

    "Ethical Hacking": {
        "course": "Ethical Hacking Fundamentals",
        "topics": [
            "Reconnaissance",
            "Vulnerability Assessment",
            "Web Security",
            "Network Security",
            "Penetration Testing Concepts"
        ]
    },

    "Risk Management": {
        "course": "Cybersecurity Risk Management",
        "topics": [
            "Risk Identification",
            "Risk Assessment",
            "Risk Mitigation",
            "Security Policies"
        ]
    },

    "Git": {
        "course": "Git & GitHub",
        "topics": [
            "Git Fundamentals",
            "Repositories",
            "Branches",
            "Commits",
            "Pull Requests"
        ]
    },

    "HTML": {
        "course": "HTML & Web Fundamentals",
        "topics": [
            "HTML Structure",
            "Forms",
            "Tables",
            "Semantic HTML",
            "Accessibility"
        ]
    },

    "CSS": {
        "course": "Modern CSS",
        "topics": [
            "CSS Fundamentals",
            "Flexbox",
            "Grid",
            "Responsive Design",
            "Animations"
        ]
    },

    "JavaScript": {
        "course": "JavaScript for Web Development",
        "topics": [
            "JavaScript Fundamentals",
            "DOM",
            "Events",
            "Fetch API",
            "Async JavaScript"
        ]
    },

    "Flask": {
        "course": "Flask Web Development",
        "topics": [
            "Flask Fundamentals",
            "Routes",
            "Templates",
            "Forms",
            "Database Integration",
            "Authentication"
        ]
    },

    "REST API": {
        "course": "REST API Development",
        "topics": [
            "REST Fundamentals",
            "HTTP Methods",
            "JSON",
            "API Authentication",
            "API Integration"
        ]
    },

    "Communication": {
        "course": "Professional Communication",
        "topics": [
            "Written Communication",
            "Presentation Skills",
            "Interview Communication",
            "Business Communication"
        ]
    },

    "Problem Solving": {
        "course": "Problem Solving & Analytical Thinking",
        "topics": [
            "Logical Thinking",
            "Analytical Thinking",
            "Problem Decomposition",
            "Decision Making"
        ]
    },

    "Business Analysis": {
        "course": "Business Analysis Fundamentals",
        "topics": [
            "Requirements Gathering",
            "Business Requirements",
            "Process Analysis",
            "Stakeholder Management",
            "Documentation"
        ]
    }
}


# =========================================================
# NORMALIZE SKILL NAME
# =========================================================

def _normalize_skill_name(skill):

    if skill is None:
        return ""

    return " ".join(
        str(skill)
        .strip()
        .lower()
        .split()
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
# GET LEARNING EVIDENCE
# =========================================================

def get_learning_evidence(student):

    """
    Returns the highest saved learning progress for
    each skill.

    Example:

        Communication -> 100
        Python        -> 60
        SQL           -> 25
    """

    evidence = {}

    if not student:
        return evidence

    try:
        progress_items = get_student_learning_progress(student)
    except Exception:
        progress_items = []

    for item in progress_items:

        skill = _normalize_skill_name(
            getattr(item, "skill", "")
        )

        if not skill:
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
            min(100, progress)
        )

        current = evidence.get(
            skill,
            0
        )

        if progress > current:
            evidence[skill] = progress

    return evidence


# =========================================================
# GET LEARNING DURATION
# =========================================================

def get_learning_duration(gap):

    gap = _safe_number(gap)

    if gap >= 51:
        return "6-8 weeks"

    elif gap >= 26:
        return "4-6 weeks"

    elif gap >= 11:
        return "2-4 weeks"

    elif gap > 0:
        return "1-2 weeks"

    return "Completed"


# =========================================================
# GET LEARNING PRIORITY
# =========================================================

def get_learning_priority(gap):

    gap = _safe_number(gap)

    if gap > 50:
        return "Critical"

    elif gap > 25:
        return "High"

    elif gap > 10:
        return "Medium"

    return "Low"


# =========================================================
# GET LEARNING RESOURCE
# =========================================================

def get_learning_resource(skill):

    skill = str(skill or "").strip()

    resource = LEARNING_RESOURCES.get(skill)

    if resource:
        return resource

    return {
        "course": f"{skill} Fundamentals",
        "topics": [
            f"{skill} Fundamentals",
            f"Intermediate {skill}",
            f"Advanced {skill}",
            f"Practical {skill} Projects"
        ]
    }


# =========================================================
# GET PRIORITIZED GAPS
# =========================================================

def get_prioritized_gaps(student, career):

    if not student or not career:
        return []

    gaps = calculate_skill_gaps(
        student,
        career
    )

    if not gaps:
        return []

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    gaps.sort(
        key=lambda item: (
            priority_order.get(
                item.get("priority"),
                5
            ),
            -_safe_number(
                item.get("gap", 0)
            )
        )
    )

    return gaps


# =========================================================
# GENERATE LEARNING PATH
# =========================================================

def generate_learning_path(student, career):

    if not student or not career:
        return []

    gaps = get_prioritized_gaps(
        student,
        career
    )

    # -----------------------------------------------------
    # IMPORTANT
    #
    # Only skills with an actual remaining gap are
    # included.
    #
    # If Communication becomes:
    #
    # Current  = 100
    # Required = 70
    # Gap      = 0
    #
    # it will NOT appear here.
    # -----------------------------------------------------

    gaps = [

        item

        for item in gaps

        if _safe_number(
            item.get("gap", 0)
        ) > 0

    ]

    learning_path = []

    learning_evidence = get_learning_evidence(
        student
    )

    for index, item in enumerate(
        gaps,
        start=1
    ):

        skill = str(
            item.get(
                "skill",
                "Unknown Skill"
            )
        ).strip()

        current = _safe_number(
            item.get(
                "current",
                0
            )
        )

        required = _safe_number(
            item.get(
                "required",
                0
            )
        )

        gap = _safe_number(
            item.get(
                "gap",
                0
            )
        )

        # -------------------------------------------------
        # LEARNING EVIDENCE
        # -------------------------------------------------

        evidence = learning_evidence.get(
            _normalize_skill_name(skill),
            0
        )

        # The skill-gap service should already include
        # learning evidence. This extra check prevents
        # stale values from producing an incorrect path.
        if evidence > current:
            current = evidence

        # Recalculate remaining gap safely.
        gap = max(
            0,
            required - current
        )

        # If learning evidence has closed the gap,
        # do not add the skill to the path.
        if gap <= 0:
            continue

        priority = item.get(
            "priority"
        )

        # Recalculate priority using the effective gap.
        priority = get_learning_priority(
            gap
        )

        duration = get_learning_duration(
            gap
        )

        resource = get_learning_resource(
            skill
        )

        learning_path.append({

            "step": index,

            "skill": skill,

            "current": int(
                round(current)
            ),

            "required": int(
                round(required)
            ),

            "gap": int(
                round(gap)
            ),

            "percentage": item.get(
                "percentage",
                0
            ),

            "status": item.get(
                "status",
                "Needs Improvement"
            ),

            "priority": priority,

            "duration": duration,

            "course": resource.get(
                "course",
                f"{skill} Fundamentals"
            ),

            "topics": resource.get(
                "topics",
                []
            ),

            "learning_status": "Not Started",

            "progress_percentage": int(
                round(evidence)
            )

        })

    # Re-number after any completed skills were removed.
    for index, item in enumerate(
        learning_path,
        start=1
    ):
        item["step"] = index

    return learning_path


# =========================================================
# CREATE COMPLETE ROADMAP
# =========================================================

def create_complete_roadmap(student, career):

    path = generate_learning_path(
        student,
        career
    )

    roadmap = []

    for index, item in enumerate(
        path,
        start=1
    ):

        roadmap.append({

            "step": index,

            "skill": item.get(
                "skill",
                "Unknown Skill"
            ),

            "current": item.get(
                "current",
                0
            ),

            "required": item.get(
                "required",
                0
            ),

            "gap": item.get(
                "gap",
                0
            ),

            "priority": item.get(
                "priority",
                "Low"
            ),

            "duration": item.get(
                "duration",
                "1-2 weeks"
            ),

            "course": item.get(
                "course",
                ""
            ),

            "topics": item.get(
                "topics",
                []
            ),

            "status": item.get(
                "learning_status",
                "Not Started"
            ),

            "progress_percentage": item.get(
                "progress_percentage",
                0
            )
        })

    return roadmap


# =========================================================
# GET NEXT LEARNING STEP
# =========================================================

def get_next_learning_step(student, career):

    path = generate_learning_path(
        student,
        career
    )

    if not path:
        return None

    return path[0]


# =========================================================
# GET LEARNING SUMMARY
# =========================================================

def get_learning_summary(student, career):

    path = generate_learning_path(
        student,
        career
    )

    if not path:

        return {
            "total_steps": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "message": (
                "You have completed all required "
                "skills!"
            )
        }

    return {

        "total_steps": len(path),

        "critical": sum(
            1
            for item in path
            if item.get(
                "priority"
            ) == "Critical"
        ),

        "high": sum(
            1
            for item in path
            if item.get(
                "priority"
            ) == "High"
        ),

        "medium": sum(
            1
            for item in path
            if item.get(
                "priority"
            ) == "Medium"
        ),

        "low": sum(
            1
            for item in path
            if item.get(
                "priority"
            ) == "Low"
        ),

        "message": (
            f"{len(path)} skills need improvement "
            f"for your {career} career goal."
        )
    }