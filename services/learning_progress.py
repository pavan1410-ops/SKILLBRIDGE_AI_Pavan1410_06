# =========================================================
# SKILLBRIDGE AI
# LEARNING PROGRESS SERVICE
# =========================================================

from datetime import datetime

from extensions import db
from models.learning_progress import LearningProgress


# ---------------------------------------------------------
# GET OR CREATE LEARNING ITEM
# ---------------------------------------------------------

def get_or_create_learning_item(student, skill, course_name):
    """
    Find an existing learning-progress record.

    If it does not exist, create a new one with:
        Status = Not Started
        Progress = 0%
    """

    item = LearningProgress.query.filter_by(
        student_id=student.id,
        skill=skill,
        course_name=course_name
    ).first()

    if item:
        return item

    item = LearningProgress(
        student_id=student.id,
        skill=skill,
        course_name=course_name,
        status="Not Started",
        progress_percentage=0
    )

    db.session.add(item)
    db.session.commit()

    return item


# ---------------------------------------------------------
# UPDATE LEARNING PROGRESS
# ---------------------------------------------------------

def update_learning_progress(
    student,
    skill,
    course_name,
    progress_percentage
):
    """
    Update the progress of a learning item.

    0%   -> Not Started
    1-99 -> In Progress
    100% -> Completed
    """

    # Make sure percentage is an integer
    try:
        progress_percentage = int(progress_percentage)
    except (TypeError, ValueError):
        progress_percentage = 0

    # Keep value between 0 and 100
    progress_percentage = max(
        0,
        min(100, progress_percentage)
    )

    item = LearningProgress.query.filter_by(
        student_id=student.id,
        skill=skill,
        course_name=course_name
    ).first()

    # Create if it doesn't exist
    if item is None:
        item = LearningProgress(
            student_id=student.id,
            skill=skill,
            course_name=course_name
        )

        db.session.add(item)

    # Update percentage
    item.progress_percentage = progress_percentage

    # Update status and dates
    if progress_percentage == 0:

        item.status = "Not Started"

        item.started_at = None
        item.completed_at = None

    elif progress_percentage < 100:

        item.status = "In Progress"

        if item.started_at is None:
            item.started_at = datetime.utcnow()

        item.completed_at = None

    else:

        item.status = "Completed"

        if item.started_at is None:
            item.started_at = datetime.utcnow()

        if item.completed_at is None:
            item.completed_at = datetime.utcnow()

    item.updated_at = datetime.utcnow()

    db.session.commit()

    return item


# ---------------------------------------------------------
# COMPLETE LEARNING ITEM
# ---------------------------------------------------------

def complete_learning_item(
    student,
    skill,
    course_name
):
    """
    Mark a learning item as 100% completed.
    """

    return update_learning_progress(
        student=student,
        skill=skill,
        course_name=course_name,
        progress_percentage=100
    )


# ---------------------------------------------------------
# GET STUDENT LEARNING PROGRESS
# ---------------------------------------------------------

def get_student_learning_progress(student):
    """
    Return all learning-progress records
    belonging to the student.
    """

    return LearningProgress.query.filter_by(
        student_id=student.id
    ).order_by(
        LearningProgress.created_at.asc()
    ).all()


# ---------------------------------------------------------
# LEARNING SUMMARY
# ---------------------------------------------------------

def get_learning_summary(student):
    """
    Return overall learning progress statistics.
    """

    items = get_student_learning_progress(student)

    total = len(items)

    completed = sum(
        1
        for item in items
        if item.status == "Completed"
    )

    in_progress = sum(
        1
        for item in items
        if item.status == "In Progress"
    )

    not_started = sum(
        1
        for item in items
        if item.status == "Not Started"
    )

    if total > 0:

        average_progress = round(
            sum(
                item.progress_percentage
                for item in items
            ) / total,
            2
        )

    else:

        average_progress = 0

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": not_started,
        "average_progress": average_progress
    }