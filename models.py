from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum, UniqueConstraint, Index

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
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    role = db.Column(Enum(Role), nullable=False, default=Role.STUDENT)

    classes = db.relationship('Class', secondary='enrollment', back_populates='users', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username


class Enrollment(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'class_id'),
        UniqueConstraint('user_id', 'course_id'),
    )

    enroll_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())


class Class(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_students = db.Column(db.Integer, nullable=False, default=25)

    course = db.relationship('Course', backref='classes', lazy=True)
    instructor = db.relationship('User', foreign_keys=[instructor_id], lazy=True)
    users = db.relationship('User', secondary='enrollment', back_populates='classes', lazy=True)

    def __str__(self):
        return self.name


class Course(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    level = db.Column(Enum(Level), nullable=False)
    status = db.Column(Enum(Status), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        course = [
            {
                "name": "Introduction to Digital Marketing",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Learn the fundamentals of digital marketing, including SEO, social media marketing, and content creation.",
                "price": 500000
            },
            {
                "name": "Web Development Basics",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Get started with web development, covering HTML, CSS, and basic JavaScript to build your first website.",
                "price": 400000
            },
            {
                "name": "Advanced Python Programming",
                "level": "ADVANCED",
                "status": "ONLINE",
                "description": "Master advanced Python concepts including decorators, generators, and working with APIs.",
                "price": 800000
            },
            {
                "name": "Creative Writing for Beginners",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Unleash your creativity and learn the basics of writing fiction, poetry, and short stories.",
                "price": 30000000
            },
            {
                "name": "Social Media Marketing for Business",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": "Learn how to use social media to grow your business, engage with customers, and increase sales.",
                "price": 60000000
            },
            {
                "name": "Data Science with R",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": "Dive into data science using the R programming language, covering data cleaning, analysis, and visualization.",
                "price": 70
            },
            {
                "name": "Mobile App Development with Flutter",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": "Learn how to build mobile applications for both Android and iOS using Flutter and Dart.",
                "price": 70
            },
            {
                "name": "Public Speaking and Communication Skills",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Develop your public speaking skills and learn how to communicate effectively in front of an audience.",
                "price": 50
            },
            {
                "name": "Graphic Design Fundamentals",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Learn the basics of graphic design, including color theory, typography, and using design software like Adobe Photoshop.",
                "price": 50
            },
            {
                "name": "Project Management for Beginners",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": "Understand the basics of project management, from planning to execution, and how to manage teams and timelines.",
                "price": 60
            }
        ]

        classes = [
            {
                "name": "IT1",
                "course_id": 1,
                "instructor_id": 1,
                "max_students": 18
            },
            {
                "name": "IT2",
                "course_id": 1,
                "instructor_id": 2,
                "max_students": 18
            },
            {
                "name": "IT3",
                "course_id": 2,
                "instructor_id": 3,
                "max_students": 18
            },
            {
                "name": "IT4",
                "course_id": 2,
                "instructor_id": 4,
                "max_students": 18
            },
            {
                "name": "IT5",
                "course_id": 3,
                "instructor_id": 5,
                "max_students": 18
            },
            {
                "name": "IT6",
                "course_id": 3,
                "instructor_id": 6,
                "max_students": 18
            },
            {
                "name": "IT7",
                "course_id": 4,
                "instructor_id": 7,
                "max_students": 18
            },
            {
                "name": "IT8",
                "course_id": 4,
                "instructor_id": 8,
                "max_students": 18
            },
            {
                "name": "IT9",
                "course_id": 5,
                "instructor_id": 9,
                "max_students": 18
            },
            {
                "name": "IT10",
                "course_id": 5,
                "instructor_id": 10,
                "max_students": 18
            },
            {
                "name": "IT11",
                "course_id": 6,
                "instructor_id": 1,
                "max_students": 18
            },
            {
                "name": "IT12",
                "course_id": 6,
                "instructor_id": 2,
                "max_students": 18
            },
            {
                "name": "IT13",
                "course_id": 7,
                "instructor_id": 3,
                "max_students": 18
            },
            {
                "name": "IT14",
                "course_id": 7,
                "instructor_id": 4,
                "max_students": 18
            },
            {
                "name": "IT15",
                "course_id": 8,
                "instructor_id": 5,
                "max_students": 18
            },
            {
                "name": "IT16",
                "course_id": 8,
                "instructor_id": 6,
                "max_students": 18
            },
            {
                "name": "IT17",
                "course_id": 9,
                "instructor_id": 7,
                "max_students": 18
            },
            {
                "name": "IT18",
                "course_id": 9,
                "instructor_id": 8,
                "max_students": 18
            },
            {
                "name": "IT19",
                "course_id": 10,
                "instructor_id": 9,
                "max_students": 18
            },
            {
                "name": "IT20",
                "course_id": 10,
                "instructor_id": 10,
                "max_students": 18
            }
        ]

        for cls in classes:
            new_class = Class(**cls)
            db.session.add(new_class)

        for c in course:
            new_course = Course(**c)
            db.session.add(new_course)
        users = [
            {"username": "instructor_alan", "password": "1", "name": "Alan Peterson", "role": Role.INSTRUCTOR},
            {"username": "instructor_maria", "password": "1", "name": "Maria Valdez", "role": Role.INSTRUCTOR},
            {"username": "instructor_jordan", "password": "1", "name": "Jordan Blake", "role": Role.INSTRUCTOR},
            {"username": "instructor_sophia", "password": "1", "name": "Sophia Kim", "role": Role.INSTRUCTOR},
            {"username": "instructor_derek", "password": "1", "name": "Derek Lawson", "role": Role.INSTRUCTOR},
            {"username": "instructor_linda", "password": "1", "name": "Linda Chen", "role": Role.INSTRUCTOR},
            {"username": "instructor_marcus", "password": "1", "name": "Marcus Allen", "role": Role.INSTRUCTOR},
            {"username": "instructor_nora", "password": "1", "name": "Nora Singh", "role": Role.INSTRUCTOR},
            {"username": "instructor_victor", "password": "1", "name": "Victor Santos", "role": Role.INSTRUCTOR},
            {"username": "instructor_hannah", "password": "1", "name": "Hannah Brooks", "role": Role.INSTRUCTOR},
            {"username": "admin", "password": "1", "role": Role.ADMIN},
            {"username": "student", "password": "1", "role": Role.STUDENT},
            {"username": "student2", "password": "1", "role": Role.STUDENT},
            {"username": "student3", "password": "1", "role": Role.STUDENT},
        ]
        for u in users:
            user = User(username=u['username'], role=u['role'], name=u.get('name', 'User'))
            user.set_password(u['password'])
            db.session.add(user)

        db.session.commit()
