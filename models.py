import datetime
from functools import wraps

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum, UniqueConstraint, Index
from datetime import datetime

from __init__ import db, app
from enums import Role, Level, Mode, Status


def only_current_user(user_id):
    from flask_login import current_user
    if user_id is None or current_user.id != int(user_id):
        return False
    return True


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    avatar = db.Column(db.String(255), nullable=True,
                       default="https://res.cloudinary.com/dkjmnoilv/image/upload/v1762911447/cld-sample.jpg")
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    role = db.Column(Enum(Role), nullable=False, default=Role.STUDENT)

    classes = db.relationship('Class', secondary='enrollment', back_populates='users', lazy=True)
    receipts = db.relationship('Receipt', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'), nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'class_id'),
        UniqueConstraint('user_id', 'course_id'),
    )

    enroll_date = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    status = db.Column(Enum(Status), nullable=False, default=Status.PENDING)
    amount = db.Column(db.Float, nullable=False, default=0.0)

    enrollments = db.relationship('Enrollment', backref='receipt', lazy=True)


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_students = db.Column(db.Integer, nullable=False, default=25)

    course = db.relationship('Course', backref='classes', lazy=True)
    instructor = db.relationship('User', foreign_keys=[instructor_id], lazy=True)
    users = db.relationship('User', secondary='enrollment', back_populates='classes', lazy=True)

    def __str__(self):
        return self.name


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(255), nullable=False)
    level = db.Column(Enum(Level), nullable=False)
    status = db.Column(Enum(Mode), nullable=False)
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
                "name": "Nền tảng Ngữ pháp Tiếng Anh",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": (
                    "Khóa học cung cấp kiến thức nền tảng về ngữ pháp tiếng Anh, tập trung vào cấu trúc câu, các thì cơ bản, "
                    "từ loại và những lỗi phổ biến người học thường gặp. Học viên được hướng dẫn qua bài tập thực hành, ví dụ "
                    "gần gũi đời sống và phương pháp áp dụng ngữ pháp vào giao tiếp hàng ngày."
                ),
                "price": 300000
            },
            {
                "name": "Tiếng Anh Giao Tiếp Hằng Ngày",
                "level": "BEGINNER",
                "status": "OFFLINE",
                "description": (
                    "Khóa học giúp học viên tự tin giao tiếp trong các tình huống thông dụng như chào hỏi, trò chuyện ngắn, "
                    "hỏi thông tin, và bày tỏ ý kiến. Học viên được luyện tập qua các hoạt động đóng vai, làm việc nhóm và "
                    "tương tác trực tiếp với giảng viên."
                ),
                "price": 350000
            },
            {
                "name": "Luyện Phát Âm và Ngữ Điệu Tiếng Anh",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": (
                    "Khóa học tập trung nâng cao khả năng phát âm rõ ràng và tự nhiên. Nội dung bao gồm trọng âm, ngữ điệu, "
                    "nhịp điệu và các lỗi phát âm thường gặp. Học viên được luyện giọng qua các bài tập ghi âm, phân tích "
                    "phiên âm và các hoạt động thực hành có hướng dẫn."
                ),
                "price": 400000
            },
            {
                "name": "Tiếng Anh Giao Tiếp Công Sở",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": (
                    "Khóa học phù hợp cho nhân sự văn phòng, trang bị kỹ năng viết email, từ vựng kinh doanh, tham gia cuộc "
                    "họp, thương lượng và trình bày trong môi trường chuyên nghiệp. Học viên được thực hành qua các tình huống "
                    "mô phỏng sát thực tế."
                ),
                "price": 500000
            },
            {
                "name": "Luyện Thi IELTS Academic",
                "level": "ADVANCED",
                "status": "OFFLINE",
                "description": (
                    "Khóa học toàn diện dành cho học viên chuẩn bị thi IELTS Academic, bao gồm đầy đủ 4 kỹ năng Listening, "
                    "Reading, Writing và Speaking. Ngoài chiến thuật làm bài, học viên được luyện đề, chấm điểm chi tiết và "
                    "nhận nhận xét cá nhân để cải thiện điểm số hiệu quả."
                ),
                "price": 2500000
            },
            {
                "name": "Kỹ Năng Viết Học Thuật Tiếng Anh",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": (
                    "Khóa học hướng dẫn học viên viết đoạn văn và bài luận học thuật theo chuẩn quốc tế, bao gồm cách phát "
                    "triển ý, viết luận điểm, liên kết ý, và chỉnh sửa nội dung. Học viên sẽ hoàn thành nhiều bài viết và được "
                    "giảng viên phản hồi chi tiết."
                ),
                "price": 450000
            },
            {
                "name": "Luyện Thi TOEIC Listening & Reading",
                "level": "INTERMEDIATE",
                "status": "ONLINE",
                "description": (
                    "Khóa học giúp học viên cải thiện điểm TOEIC qua các bài tập nghe – đọc chuyên sâu, chiến thuật làm bài, "
                    "tăng tốc độ xử lý thông tin và rèn luyện từ vựng chuyên dụng. Chương trình bao gồm bài kiểm tra thử và "
                    "đánh giá tiến độ định kỳ."
                ),
                "price": 550000
            },
            {
                "name": "Từ Vựng và Cách Dùng Tiếng Anh Nâng Cao",
                "level": "ADVANCED",
                "status": "ONLINE",
                "description": (
                    "Khóa học mở rộng vốn từ thông qua các chủ đề học thuật và đời sống, kèm theo thành ngữ, cụm động từ và "
                    "collocations được người bản xứ sử dụng thường xuyên. Học viên sẽ luyện tập hàng tuần qua bài đọc, bài nói "
                    "và bài kiểm tra từ vựng."
                ),
                "price": 400000
            },
            {
                "name": "Kỹ Năng Thuyết Trình Chuyên Nghiệp Bằng Tiếng Anh",
                "level": "ADVANCED",
                "status": "OFFLINE",
                "description": (
                    "Khóa học rèn luyện kỹ năng xây dựng bài nói, sử dụng slide hiệu quả, ngôn ngữ thuyết phục, phong thái "
                    "trình bày và xử lý câu hỏi. Học viên sẽ thực hiện nhiều bài thuyết trình và nhận phản hồi chi tiết để "
                    "cải thiện theo từng buổi."
                ),
                "price": 1200000
            },
            {
                "name": "Tiếng Anh cho Dịch vụ Khách hàng & Du lịch",
                "level": "BEGINNER",
                "status": "ONLINE",
                "description": (
                    "Khóa học dành cho người làm ngành khách sạn – dịch vụ – du lịch, tập trung vào giao tiếp chuyên nghiệp "
                    "với khách quốc tế. Nội dung bao gồm chào hỏi, xử lý yêu cầu, giải quyết vấn đề, và từ vựng chuyên ngành "
                    "dùng trong khách sạn, nhà hàng và dịch vụ du lịch."
                ),
                "price": 300000
            }
        ]

        classes = [
            {"name": "EN1", "course_id": 1, "instructor_id": 1, "max_students": 25},
            {"name": "EN2", "course_id": 1, "instructor_id": 5, "max_students": 25},
            {"name": "EN3", "course_id": 1, "instructor_id": 12, "max_students": 25},

            {"name": "EN4", "course_id": 2, "instructor_id": 3, "max_students": 25},
            {"name": "EN5", "course_id": 2, "instructor_id": 9, "max_students": 25},

            {"name": "EN6", "course_id": 3, "instructor_id": 7, "max_students": 25},
            {"name": "EN7", "course_id": 3, "instructor_id": 16, "max_students": 25},

            {"name": "EN8", "course_id": 4, "instructor_id": 4, "max_students": 25},
            {"name": "EN9", "course_id": 4, "instructor_id": 14, "max_students": 25},

            {"name": "EN10", "course_id": 5, "instructor_id": 2, "max_students": 25},
            {"name": "EN11", "course_id": 5, "instructor_id": 18, "max_students": 25},

            {"name": "EN12", "course_id": 6, "instructor_id": 6, "max_students": 25},
            {"name": "EN13", "course_id": 6, "instructor_id": 20, "max_students": 25},

            {"name": "EN14", "course_id": 7, "instructor_id": 8, "max_students": 25},
            {"name": "EN15", "course_id": 7, "instructor_id": 11, "max_students": 25},

            {"name": "EN16", "course_id": 8, "instructor_id": 10, "max_students": 25},
            {"name": "EN17", "course_id": 8, "instructor_id": 15, "max_students": 25},

            {"name": "EN18", "course_id": 9, "instructor_id": 13, "max_students": 25},
            {"name": "EN19", "course_id": 9, "instructor_id": 19, "max_students": 25},

            {"name": "EN20", "course_id": 10, "instructor_id": 17, "max_students": 25},
        ]

        for cls in classes:
            new_class = Class(**cls)
            db.session.add(new_class)

        for c in course:
            new_course = Course(**c)
            db.session.add(new_course)
        users = [
            {"username": "instructor_thu", "password": "1", "name": "Anh Thư", "role": Role.INSTRUCTOR},
            {"username": "instructor_tam", "password": "1", "name": "Minh Tâm", "role": Role.INSTRUCTOR},
            {"username": "instructor_lan", "password": "1", "name": "Phương Lan", "role": Role.INSTRUCTOR},
            {"username": "instructor_linh", "password": "1", "name": "Khánh Linh", "role": Role.INSTRUCTOR},
            {"username": "instructor_phuc", "password": "1", "name": "Trần Phúc", "role": Role.INSTRUCTOR},

            {"username": "instructor_nhu", "password": "1", "name": "Huỳnh Như", "role": Role.INSTRUCTOR},
            {"username": "instructor_truong", "password": "1", "name": "Văn Trường", "role": Role.INSTRUCTOR},
            {"username": "instructor_nam", "password": "1", "name": "Hoài Nam", "role": Role.INSTRUCTOR},
            {"username": "instructor_kiet", "password": "1", "name": "Anh Kiệt", "role": Role.INSTRUCTOR},
            {"username": "instructor_tram", "password": "1", "name": "Bảo Trâm", "role": Role.INSTRUCTOR},

            {"username": "instructor_my", "password": "1", "name": "Hiền My", "role": Role.INSTRUCTOR},
            {"username": "instructor_han", "password": "1", "name": "Gia Hân", "role": Role.INSTRUCTOR},
            {"username": "instructor_thien", "password": "1", "name": "Đức Thiện", "role": Role.INSTRUCTOR},
            {"username": "instructor_vy", "password": "1", "name": "Thảo Vy", "role": Role.INSTRUCTOR},
            {"username": "instructor_minh", "password": "1", "name": "Lê Minh", "role": Role.INSTRUCTOR},

            {"username": "instructor_khanh", "password": "1", "name": "Nhã Khánh", "role": Role.INSTRUCTOR},
            {"username": "instructor_loan", "password": "1", "name": "Hồng Loan", "role": Role.INSTRUCTOR},
            {"username": "instructor_duy", "password": "1", "name": "Quang Duy", "role": Role.INSTRUCTOR},
            {"username": "instructor_tam2", "password": "1", "name": "Thanh Tâm", "role": Role.INSTRUCTOR},
            {"username": "instructor_an", "password": "1", "name": "Tường An", "role": Role.INSTRUCTOR},

            {"username": "admin", "password": "1", "role": Role.ADMIN},
            {"username": "student", "password": "1", "role": Role.STUDENT},
            {"username": "student2", "password": "1", "role": Role.STUDENT},
            {"username": "student3", "password": "1", "role": Role.STUDENT},
            {"username": "cashier", "password": "1", "role": Role.CASHIER},
        ]
        for u in users:
            user = User(username=u['username'], role=u['role'], name=u.get('name', 'User'))
            user.set_password(u['password'])
            db.session.add(user)

        db.session.commit()
