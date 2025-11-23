from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum

from __init__ import db, app
from enums import Role, Level, Status


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class User(BaseModel, UserMixin):
    avatar = db.Column(db.String(255), nullable=True,
                       default="https://res.cloudinary.com/dkjmnoilv/image/upload/v1762911447/cld-sample.jpg")
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum(Role), nullable=False, default=Role.STUDENT)

    classes = db.relationship('Class', secondary='enrollment', back_populates='users', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username


class Enrollment(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, primary_key=True)


class Class(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    max_students = db.Column(db.Integer, nullable=False, default=25)

    course = db.relationship('Course', backref='classes', lazy=True)
    users = db.relationship('User', secondary='enrollment', back_populates='classes', lazy='dynamic')

    def __str__(self):
        return self.name


class Course(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    level = db.Column(Enum(Level), nullable=False)
    status = db.Column(Enum(Status), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.name

# if __name__ == "__main__":
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#         course = [
#             {
#                 "name": "Basic English Grammar",
#                 "level": "BEGINNER",
#                 "status": "ONLINE",
#                 "description": "Learn the fundamentals of English grammar, including sentence structure, tenses, and basic vocabulary."
#             },
#             {
#                 "name": "Conversational English for Beginners",
#                 "level": "BEGINNER",
#                 "status": "OFFLINE",
#                 "description": "Improve your speaking skills and build confidence in basic conversations with native English speakers."
#             },
#             {
#                 "name": "Intermediate English Writing Skills",
#                 "level": "INTERMEDIATE",
#                 "status": "ONLINE",
#                 "description": "Enhance your writing skills by focusing on essays, emails, and reports with a strong emphasis on clarity and structure."
#             },
#             {
#                 "name": "English for Business Communication",
#                 "level": "INTERMEDIATE",
#                 "status": "ONLINE",
#                 "description": "Learn professional English communication for business settings, including presentations, meetings, and email etiquette."
#             },
#             {
#                 "name": "English Listening Comprehension",
#                 "level": "BEGINNER",
#                 "status": "OFFLINE",
#                 "description": "Develop your listening skills with a focus on understanding everyday English conversations, news broadcasts, and podcasts."
#             },
#             {
#                 "name": "Advanced English Vocabulary Building",
#                 "level": "ADVANCED",
#                 "status": "ONLINE",
#                 "description": "Expand your English vocabulary to an advanced level, focusing on idioms, phrasal verbs, and academic language."
#             },
#             {
#                 "name": "Pronunciation and Accent Reduction",
#                 "level": "INTERMEDIATE",
#                 "status": "OFFLINE",
#                 "description": "Work on reducing your accent and improving pronunciation for clearer and more confident speech."
#             },
#             {
#                 "name": "English for Travel and Tourism",
#                 "level": "BEGINNER",
#                 "status": "ONLINE",
#                 "description": "Learn English phrases and vocabulary useful for travel, including hotel reservations, directions, and ordering food."
#             },
#             {
#                 "name": "Academic English for University Studies",
#                 "level": "ADVANCED",
#                 "status": "ONLINE",
#                 "description": "Prepare for university-level studies in English with a focus on academic writing, reading comprehension, and research skills."
#             },
#             {
#                 "name": "English for Social Media and Networking",
#                 "level": "INTERMEDIATE",
#                 "status": "ONLINE",
#                 "description": "Learn the language and vocabulary commonly used on social media platforms and in online networking."
#             }
#         ]
#         classes = [
#             {
#                 "name": "Basic English Grammar - Session 1",
#                 "course_id": 1,
#                 "max_students": 25
#             },
#             {
#                 "name": "Conversational English for Beginners - Session 1",
#                 "course_id": 2,
#                 "max_students": 25
#             },
#             {
#                 "name": "Conversational English for Beginners - Session 2",
#                 "course_id": 2,
#                 "max_students": 25
#             },
#             {
#                 "name": "Intermediate English Writing Skills - Session 1",
#                 "course_id": 3,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Business Communication - Session 1",
#                 "course_id": 4,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Business Communication - Session 2",
#                 "course_id": 4,
#                 "max_students": 25
#             },
#             {
#                 "name": "English Listening Comprehension - Session 1",
#                 "course_id": 5,
#                 "max_students": 25
#             },
#             {
#                 "name": "Advanced English Vocabulary Building - Session 1",
#                 "course_id": 6,
#                 "max_students": 25
#             },
#             {
#                 "name": "Advanced English Vocabulary Building - Session 2",
#                 "course_id": 6,
#                 "max_students": 25
#             },
#             {
#                 "name": "Pronunciation and Accent Reduction - Session 1",
#                 "course_id": 7,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Travel and Tourism - Session 1",
#                 "course_id": 8,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Travel and Tourism - Session 2",
#                 "course_id": 8,
#                 "max_students": 25
#             },
#             {
#                 "name": "Academic English for University Studies - Session 1",
#                 "course_id": 9,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Social Media and Networking - Session 1",
#                 "course_id": 10,
#                 "max_students": 25
#             },
#             {
#                 "name": "English for Social Media and Networking - Session 2",
#                 "course_id": 10,
#                 "max_students": 25
#             }
#         ]
#         for cls in classes:
#             new_class = Class(**cls)
#             db.session.add(new_class)
#
#         for c in course:
#             new_course = Course(**c)
#             db.session.add(new_course)
#         users = [
#             {"username": "admin", "password": "1", "role": Role.ADMIN},
#             {"username": "student", "password": "1", "role": Role.STUDENT},
#             {"username": "instructor", "password": "1", "role": Role.INSTRUCTOR},
#         ]
#         for u in users:
#             user = User(username=u['username'], role=u['role'])
#             user.set_password(u['password'])
#             db.session.add(user)
#
#         db.session.commit()
