from models import User, Course
import hashlib
from __init__ import app


def get_user_by_id(user_id):
    return User.query.get(user_id)


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
