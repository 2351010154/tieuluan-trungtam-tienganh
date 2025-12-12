from flask_login import current_user
from sqlalchemy import func, case, select, exists
from sqlalchemy.orm import joinedload
import cloudinary.uploader
from datetime import datetime

from enums import Role, Status, ConfigKey, Level
from models import User, Course, Class, Enrollment, Receipt, Configuration
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


def get_enrollment_details_by_id(enrollment_id):
    query = db.session.query(Enrollment, Class, Course).join(
        Class, Enrollment.class_id == Class.id).join(Course, Enrollment.course_id == Course.id).filter(
        Enrollment.id == enrollment_id
    )
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


def get_users_with_receipt_status_by_class(class_id, status):
    query = db.session.query(func.count(Enrollment.id)).join(
        Receipt, Receipt.id == Enrollment.receipt_id).join(
        Class, Class.id == Enrollment.class_id).filter(
        Class.id == class_id,
        Receipt.status == status
    )
    return query


def register_course(user_id, class_id):
    class_ = get_class_by_id(class_id)
    users_in_class = get_users_with_receipt_status_by_class(class_id, Status.PAID).scalar()
    if users_in_class > class_.max_students:
        return None

    enrollment = Enrollment(
        user_id=user_id,
        class_id=class_.id,
        course_id=class_.course.id,
    )
    db.session.add(enrollment)
    db.session.flush()
    return enrollment.id


def get_monthly_revenue(month=None, year=None):
    if not month or not year:
        now = datetime.now()
        month = now.month
        year = now.year

    total = db.session.query(func.sum(Receipt.amount)).filter(
        func.extract('month', Receipt.created_at) == month,
        func.extract('year', Receipt.created_at) == year,
        Receipt.status == Status.PAID
    ).scalar()

    return total if total else 0


def get_monthly_new_students(month=None, year=None):
    if not month or not year:
        now = datetime.now()
        month = now.month
        year = now.year

    count = db.session.query(func.count(func.distinct(Enrollment.user_id))).filter(
        func.extract('month', Enrollment.enroll_date) == month,
        func.extract('year', Enrollment.enroll_date) == year
    ).scalar()

    return count if count else 0


def count_total_classes():
    return Class.query.count()


def get_revenue_stats():
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    revenue_now = get_monthly_revenue(current_month, current_year)
    revenue_last = get_monthly_revenue(last_month, last_month_year)

    if revenue_last > 0:
        growth_percent = ((revenue_now - revenue_last) / revenue_last) * 100
    elif revenue_now > 0:
        growth_percent = 100
    else:
        growth_percent = 0

    return revenue_now, round(growth_percent, 1)


def count_total_students():
    return User.query.filter(User.role == Role.STUDENT).count()


def stats_enrollment_by_level():
    query = db.session.query(Course.level, func.count(Enrollment.id)) \
        .join(Class, Class.course_id == Course.id) \
        .join(Enrollment, Enrollment.class_id == Class.id) \
        .group_by(Course.level).all()

    stats = {str(level): count for level, count in query}

    return [
        stats.get('Level.BEGINNER', 0),
        stats.get('Level.INTERMEDIATE', 0),
        stats.get('Level.ADVANCED', 0)
    ]


def stats_revenue(year, period='month'):
    query = db.session.query(
        func.extract(period, Receipt.created_at),
        func.sum(Receipt.amount)
    ).filter(
        func.extract('year', Receipt.created_at) == year,
        Receipt.status == Status.PAID
    ).group_by(func.extract(period, Receipt.created_at)).all()

    if period == 'quarter':
        data = [0] * 4
    else:
        data = [0] * 12

    for p, amount in query:
        data[int(p) - 1] = amount

    return data


def stats_students(year, period='month'):
    query = db.session.query(
        func.extract(period, Enrollment.enroll_date),
        func.count(func.distinct(Enrollment.user_id))
    ).filter(
        func.extract('year', Enrollment.enroll_date) == year
    ).group_by(func.extract(period, Enrollment.enroll_date)).all()

    if period == 'quarter':
        data = [0] * 4
    else:
        data = [0] * 12

    for p, count in query:
        data[int(p) - 1] = count

    return data


def stats_students_by_course(year):
    query = db.session.query(
        Course.name,
        func.count(Enrollment.id)
    ).join(
        Class, Class.course_id == Course.id
    ).join(
        Enrollment, Enrollment.class_id == Class.id
    ).filter(
        func.extract('year', Enrollment.enroll_date) == year
    ).group_by(Course.id, Course.name).all()

    return query


def get_all_rules():
    configs = Configuration.query.all()
    data = {c.key: c.value for c in configs}

    return {
        "max_students": data.get(ConfigKey.MAX_STUDENTS.value, 25),
        "tuition_fees": [
            {"id": ConfigKey.FEE_BEGINNER.value, "name": Level.BEGINNER.value,
             "price": data.get(ConfigKey.FEE_BEGINNER.value, 0)},
            {"id": ConfigKey.FEE_INTERMEDIATE.value, "name": Level.INTERMEDIATE.value,
             "price": data.get(ConfigKey.FEE_INTERMEDIATE.value, 0)},
            {"id": ConfigKey.FEE_ADVANCED.value, "name": Level.ADVANCED.value,
             "price": data.get(ConfigKey.FEE_ADVANCED.value, 0)}
        ]
    }


def update_rules(data):
    try:
        for key, value in data.items():
            config = Configuration.query.filter_by(key=key).first()
            if config:
                config.value = str(value)
            else:
                new_config = Configuration(key=key, value=str(value))
                db.session.add(new_config)

        level_map = {
            Level.BEGINNER: ConfigKey.FEE_BEGINNER.value,
            Level.INTERMEDIATE: ConfigKey.FEE_INTERMEDIATE.value,
            Level.ADVANCED: ConfigKey.FEE_ADVANCED.value
        }

        courses = Course.query.all()
        for c in courses:
            config_key = level_map.get(c.level)
            if config_key and config_key in data:
                c.price = float(data[config_key])

        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return False


def create_new_class(name, course_id, instructor_id):
    config_max = Configuration.query.filter_by(key=ConfigKey.MAX_STUDENTS.value).first()

    default_max = int(config_max.value) if config_max else 25

    new_class = Class(
        name=name,
        course_id=course_id,
        instructor_id=instructor_id,
        max_students=default_max
    )

    db.session.add(new_class)
    db.session.commit()
    return new_class
