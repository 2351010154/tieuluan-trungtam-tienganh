from flask_login import current_user
from sqlalchemy import func, case, select, exists
from sqlalchemy.orm import joinedload
import cloudinary.uploader

from enums import Role, Status
from models import User, Course, Class, Enrollment, Receipt
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
    query = db.session.query(Enrollment, Class, Course).join(Class, Enrollment.class_id == Class.id).join(Course,
                                                                                                          Course.id == Class.course_id).filter(
        Enrollment.user_id == user_id)
    return query


def get_enrollment_with_receipt(user_id):
    query = db.session.query(Enrollment, Class, Course, Receipt.status).join(Class,
                                                                             Enrollment.class_id == Class.id).join(
        Course, Course.id == Class.course_id).filter(
        Enrollment.user_id == user_id).outerjoin(Receipt, Receipt.id == Enrollment.receipt_id)

    query = query.filter(Enrollment.user_id == user_id)
    return query


def get_no_receipt_enrollments(user_id):
    query = db.session.query(Enrollment, Class, Course).join(Class, Enrollment.class_id == Class.id).join(Course,
                                                                                                          Enrollment.course_id == Course.id)
    query = query.filter(
        ~exists().where(
            (Receipt.id == Enrollment.receipt_id)
        ), Enrollment.user_id == user_id)
    return query.all()


def get_receipt_by_id(receipt_id):
    return db.session.query(Receipt).get(receipt_id)


def get_receipt_by_user_id(user_id):
    query = db.session.query(Receipt).filter(Receipt.user_id == user_id)
    return query


def get_enrollment_receipts_details(user_id, receipt_id, status='Pending'):
    query = db.session.query(Enrollment, Class, Course).join(
        Receipt, Receipt.id == Enrollment.receipt_id).join(
        Class, Enrollment.class_id == Class.id).join(
        Course, Enrollment.course_id == Course.id).filter(
        Receipt.user_id == user_id,
        Receipt.id == receipt_id,
        Receipt.status == status,
    )
    return query.all()


def get_enrollment(user_id, class_id):
    query = db.session.query(Enrollment).filter(Enrollment.user_id == user_id,
                                                Enrollment.class_id == class_id)
    return query.first()


def get_enrollment_by_id(enrollment_id):
    return db.session.query(Enrollment).get(enrollment_id)


def delete_enrollment(enrollment):
    try:
        receipt_id = enrollment.receipt_id
        if receipt_id is not None:
            receipt = get_receipt_by_id(receipt_id)
            db.session.delete(receipt)
        db.session.delete(enrollment)
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
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


def add_user(name, username, password_hash, role, avatar, email):
    avatar_url = None
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        avatar_url = res['secure_url']

    u = User(name=name,
             username=username,
             email=email,
             role=role,
             avatar=avatar_url)

    u.set_password(password_hash)
    db.session.add(u)
    db.session.commit()


def add_receipt(user_id, enrollment_ids, prices):
    try:
        receipt = Receipt(user_id=user_id, amount=sum([int(s) for s in prices]))
        db.session.add(receipt)
        db.session.flush()
        update_receipt_id_for_enrollments(enrollment_ids, receipt.id)
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return False


def update_receipt_id_for_enrollments(enrollment_ids, receipt_id):
    try:
        enrollments = db.session.query(Enrollment).filter(Enrollment.id.in_(enrollment_ids)).all()
        for enrollment in enrollments:
            if enrollment.receipt_id is not None:
                raise Exception("enrollment created already")
            enrollment.receipt_id = receipt_id
        db.session.commit()
        return True
    except Exception as ex:
        db.session.rollback()
        raise ex


def confirm_receipt(receipt_id):
    try:
        receipt = get_receipt_by_id(receipt_id)
        if receipt.status == Status.PAID:
            return False
        receipt.status = Status.PAID
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def get_pending_receipts_with_user():
    query = db.session.query(Receipt, User.name).join(User, Receipt.user_id == User.id).filter(
        Receipt.status == 'Pending')
    return query.all()


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
