from flask_login import current_user
from sqlalchemy import func, case, select, exists
from sqlalchemy.orm import joinedload

from enums import Role
from models import User, Course, Class, Enrollment
import hashlib
from __init__ import app, db


def get_class_by_id(class_id):
    return Class.query.get(class_id)


def get_course_by_id(course_id):
    return Course.query.get(course_id)


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_instructors():
    return User.query.filter(User.role == Role.INSTRUCTOR)


def get_enrolled_courses_id(user_id):
    query = (
        select(Course.id)
        .where(
            exists(
                select(1)
                .where(
                    Enrollment.course_id == Course.id,
                    Enrollment.user_id == user_id,
                )
            )
        )
    )
    return db.session.execute(query).scalars().all()


def get_courses_filter(level, kw, page, hide_enrolled, user_id):
    query = Course.query
    if level:
        query = query.filter(Course.level == level)
    if kw:
        query = query.filter(Course.name.contains(kw))
    if hide_enrolled:
        enrolled_ids = get_enrolled_courses_id(user_id)
        query = query.filter(Course.id.notin_(enrolled_ids))
    if page:
        page_size = app.config.get("PAGE_SIZE", 6)
        start = (page - 1) * page_size
        query = query.slice(start, start + page_size)

    return query.all()


def sum_course_level():
    row = Course.query.with_entities(
        func.count(Course.id).label('total'),
        func.sum(case(
            {Course.level == 'Beginner': 1},
            else_=0
        )),
        func.sum(case(
            {Course.level == 'Intermediate': 1},
            else_=0
        )),
        func.sum(case(
            {Course.level == 'Advanced': 1},
            else_=0
        ))
    ).first()
    return row


def get_enrollment_by_user(user_id):
    enrollment = db.session.query(Enrollment, Class, Course).join(Class, Enrollment.class_id == Class.id).join(Course,
                                                                                                               Course.id == Class.course_id).filter(
        Enrollment.user_id == user_id).all()
    return enrollment


def get_enrollment(user_id, class_id):
    enrollment = db.session.query(Enrollment).filter(Enrollment.user_id == user_id,
                                                     Enrollment.class_id == class_id).first()
    return enrollment


def delete_enrollment(enrollment):
    try:
        db.session.delete(enrollment)
        db.session.commit()
        return True
    except Exception as ex:
        return False


def count_course(level, kw, hide_enrolled, user_id):
    query = Course.query
    if level:
        query = query.filter(Course.level == level)
    if kw:
        query = query.filter(Course.name.contains(kw))
    if hide_enrolled:
        enrolled_ids = get_enrolled_courses_id(user_id)
        query = query.filter(Course.id.notin_(enrolled_ids))

    return query.count()


def get_courses():
    return Course.query.all()


def add_user(username, password_hash, role, avatar):
    u = User(name=username.strip(),
             password=str(hashlib.md5(password_hash.strip().encode('utf-8')).hexdigest), role=role, avatar=avatar)


def register_course(user_id, class_id):
    class_ = get_class_by_id(class_id)
    enrollment = Enrollment(
        user_id=user_id,
        class_id=class_.id,
        course_id=class_.course.id,
    )

    if len(class_.users) < class_.max_students:
        db.session.add(enrollment)
        return True
    return False
