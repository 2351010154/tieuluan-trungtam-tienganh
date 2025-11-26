from flask_login import current_user
from sqlalchemy import func, case
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


def get_courses_filter(level, kw, page):
    query = Course.query
    if level:
        query = query.filter(Course.level == level)
    if kw:
        query = query.filter(Course.name.contains(kw))
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


def count_course(level, kw):
    query = Course.query
    if level:
        query = query.filter(Course.level == level)
    if kw:
        query = query.filter(Course.name.contains(kw))

    return query.count()


def get_courses():
    return Course.query.all()


def add_user(username, password_hash, role, avatar):
    u = User(name=username.strip(),
             password=str(hashlib.md5(password_hash.strip().encode('utf-8')).hexdigest), role=role, avatar=avatar)


def register_course(user_id, class_id):
    user = get_user_by_id(user_id)
    course_class = get_class_by_id(class_id)
    if user and course_class:
        user.classes.append(course_class)
        return True
    return False
