import math

import resend
from flask import render_template, session, request, url_for, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from sqlalchemy.sql.coercions import expect
from werkzeug.utils import redirect
from datetime import datetime

from dao import get_enrolled_courses_id, get_users_with_receipt_status_by_class
from models import Role, only_current_user

import dao
import enums

from __init__ import app, db, login_manager, from_email
from models import User
from utils import sendEmail, level_vn


def get_sidebar_items():
    sidebar_items = {
        Role.STUDENT: [
            {
                'label': 'Trang Chủ',
                'icon_type': 'svg',
                'icon_path': '/svg/dashboard.html',
                'path': '/home',
                'url_name': 'home_view',
            },
            {
                'label': 'Các khoá học',
                'icon_type': 'svg',
                'icon_path': '/svg/courses.html',
                'path': '/courses',
                'url_name': 'courses_view',
            },
        ],
        Role.INSTRUCTOR: [
            {
                'label': 'Bảng điểm',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/giang-vien/bang-diem',
                'url_name': 'instructor_home_view',
            },
            {
                'label': 'Điểm danh',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/giang-vien/diem-danh',
                'url_name': 'instructor_attendance_view',
            }
        ],
        Role.CASHIER: [
            {
                'label': 'Lập hoá đơn',
                'icon_type': 'svg',
                'icon_path': '/svg/dollar.html',
                'path': '/invoice',
                'url_name': 'create_invoice_view',
            },
            {
                'label': 'Hoá đơn chờ duyệt',
                'icon_type': 'svg',
                'icon_path': '/svg/receipt.html',
                'path': '/receipts',
                'url_name': 'receipts_view',
            }
        ],
        Role.ADMIN: [
            {
                'label': 'Trang Chủ Admin',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/admins',
                'url_name': 'admin_home_view',
            },
            {
                'label': 'Báo Cáo',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/admins/baocao',
                'url_name': 'admin_baocao_view',
            },
            {
                'label': 'Quy Định',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/admins/rules',
                'url_name': 'admin_rules_view',
            }
        ]
    }
    if current_user.is_authenticated:
        return sidebar_items.get(current_user.role, [])
    return []


def get_home_page():
    sidebar_items = get_sidebar_items()
    for item in sidebar_items:
        if item['url_name']:
            return item['url_name']
    return 'index'


@app.context_processor
def common_response():
    return {
        'sidebar_items': get_sidebar_items(),
        'level_vn': level_vn,
    }


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(get_home_page()))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login_process():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        home_page = None
        return redirect(url_for(get_home_page()))
    return render_template('index.html', err_msg='Sai mật khẩu hoặc tài khoản')


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_process():
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    if password != confirm:
        err_msg = 'Mật Khẩu KHONG Khớp!'
        return render_template('register.html', err_msg=err_msg)

    avatar = request.files.get('avatar')
    email = request.form['email']
    try:
        dao.add_user(name=request.form['name'],
                     username=request.form['username'],
                     password_hash=request.form['password'],
                     email=email,
                     role=Role.STUDENT,
                     avatar=avatar)
        html_content = "<h1>Welcome to Our Platform</h1><p>Thank you for registering, {}!</p>".format(
            request.form['name'])

        sendEmail(email, "Welcome to Our Platform", html_content)

        return redirect(url_for('index'))
    except Exception as ex:
        return render_template('register.html', err_msg='He thong dang co loi')


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/home')
def home_view():
    if current_user.is_authenticated:
        return render_template('home.html', enrollment=dao.get_enrollment_with_receipt(current_user.id).all())
    return redirect(url_for('index'))


@app.route('/invoice')
def invoice_view():
    enrollment_id = request.args.get('enrollment_id', type=int)
    enrollment = dao.get_enrollment_details_by_id(enrollment_id)
    if enrollment:
        e, c, course = enrollment
        if current_user.is_authenticated:
            return render_template('invoice.html', enrollment=e, class_=c, course=course)
    return redirect(url_for('index'))


@app.route('/create-invoice')
def create_invoice_view():
    if current_user.is_authenticated:
        return render_template('create-invoice.html')
    return redirect(url_for('index'))


@app.route('/receipts')
def receipts_view():
    if current_user.is_authenticated:
        pending_receipts = dao.get_pending_receipts_with_user()
        return render_template('receipts.html', receipts=pending_receipts)
    return redirect(url_for('index'))


@app.route('/api/chart-data')
@login_required
def get_chart_data():
    year = request.args.get('year', type=int)
    if not year:
        year = datetime.now().year

    data = dao.stats_revenue_by_year(year)

    return jsonify(data)


@app.route('/admins')
@login_required
def admin_home_view():
    if current_user.is_authenticated and current_user.role == Role.ADMIN:
        revenue, growth = dao.get_revenue_stats()
        new_students = dao.get_monthly_new_students()
        total_classes = dao.count_total_classes()
        total_all_students = dao.count_total_students()

        current_year = datetime.now().year

        revenue_chart_data = dao.stats_revenue(current_year, period='month')
        source_chart_data = dao.stats_enrollment_by_level()

        return render_template('admin_home.html',
                               revenue=revenue,
                               growth_percent=growth,
                               new_students=new_students,
                               total_classes=total_classes,
                               total_all_students=total_all_students,
                               current_year=current_year,
                               revenue_chart_data=revenue_chart_data,
                               source_chart_data=source_chart_data)

    return redirect(url_for('index'))


@app.route('/admins/baocao')
@login_required
def admin_baocao_view():
    if current_user.role == Role.ADMIN:
        current_year = datetime.now().year
        return render_template('admin_baocao.html', current_year=current_year)
    return redirect(url_for('index'))


@app.route('/api/stats')
@login_required
def get_stats_data():
    year = request.args.get('year', default=datetime.now().year, type=int)
    report_type = request.args.get('type', default='revenue')
    period = request.args.get('period', default='month')

    if report_type == 'course':
        stats = dao.stats_students_by_course(year)

        labels = [s[0] for s in stats]
        data = [s[1] for s in stats]
        label = "Số lượng học viên"
    else:
        if period == 'quarter':
            labels = ["Quý 1", "Quý 2", "Quý 3", "Quý 4"]
        else:
            labels = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                      "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]

        if report_type == 'student':
            data = dao.stats_students(year, period)
            label = "Số lượng học viên"
        else:
            data = dao.stats_revenue(year, period)
            label = "Doanh thu (VNĐ)"

    return jsonify({
        'data': data,
        'label': label,
        'labels': labels
    })


@app.route('/admins/rules')
@login_required
def admin_rules_view():
    if current_user.role == Role.ADMIN:
        rules_data = dao.get_all_rules()
        return render_template('admin_quydinh.html', rules=rules_data)
    return redirect(url_for('index'))


@app.route('/api/rules', methods=['PUT'])
@login_required
def update_rules_api():
    if current_user.role != Role.ADMIN:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json

    if dao.update_rules(data):
        return jsonify({'msg': 'success'})
    else:
        return jsonify({'error': 'Failed to update rules'}), 500


@app.route('/courses')
def courses_view():
    if current_user.is_authenticated:
        level = request.args.get('difficulty')
        kw = request.args.get('keyword')
        page = request.args.get('page', 1, type=int)
        hide_enrolled = request.args.get('hide_enrolled')
        return render_template('courses.html', pages=math.ceil(
            dao.count_course(level, kw, hide_enrolled, current_user.id) / app.config["PAGE_SIZE"]),
                               courses=dao.get_courses_filter(level, kw, page, hide_enrolled, current_user.id)
                               , levels=enums.Level, total_courses=dao.sum_course_level())
    return redirect(url_for('index'))


@app.route('/api/courses', methods=['GET'])
def get_courses_api():
    courses = dao.get_courses()
    if courses:
        course_list = []
        for c in courses:
            course_list.append({
                'id': c.id,
                'name': c.name,
                'price': c.price,
                'level': c.level.value,
                'status': c.status.value,
                'description': c.description
            })
        return jsonify(course_list)
    return jsonify({
        'error': 'courses not found'
    })


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_api(course_id):
    course = dao.get_course_by_id(course_id)
    if course:
        return jsonify(
            {
                'id': course.id,
                'name': course.name,
                'price': course.price,
                'level': course.level.value,
                'status': course.status.value,
                'description': course.description
            }
        )
    else:
        return jsonify({
            'error': 'course not found'
        })


@app.route('/api/courses/<int:course_id>/classes', methods=['GET'])
def get_classes_by_course_api(course_id):
    classes = dao.get_course_by_id(course_id).classes

    if classes:
        class_list = []
        for c in classes:
            class_list.append({
                'id': c.id,
                'instructor': c.instructor.name,
                'name': c.name,
                'max_students': c.max_students,
                'current_size': get_users_with_receipt_status_by_class(c.id, 'PAID').scalar(),
                'course_id': c.course.id,
                'price': c.course.price
            })
        return jsonify(class_list)
    return jsonify({
        'error': 'Classes not found'
    })


@app.route('/giang-vien/bang-diem')
@login_required
def instructor_home_view():
    if current_user.role != Role.INSTRUCTOR:
        return redirect(url_for('index'))
    classes = dao.get_classes_by_instructor(current_user.id)
    select_class_id = request.args.get('class_id', type=int)
    transcript = []
    if not select_class_id and classes:
        select_class_id = classes[0].id
    if select_class_id:
        transcript = dao.get_transcript(select_class_id)
    return render_template('giaovienindex.html', classes=classes, transcript=transcript,
                           select_class_id=select_class_id)


@app.route('/giang-vien/diem-danh')
@login_required
def instructor_attendance_view():
    if current_user.role != Role.INSTRUCTOR:
        return redirect(url_for('index'))
    classes = dao.get_classes_by_instructor(current_user.id)
    select_class_id = request.args.get('class_id', type=int)
    date_str = request.args.get('date')

    if not select_class_id and classes:
        select_class_id = classes[0].id

    select_date = datetime.now().date()
    if date_str:
        try:
            select_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    attendance_data = []
    select_class_name = ""
    if select_class_id:
        cls = dao.get_class_by_id(select_class_id)
        if cls:
            select_class_name = f"{cls.name} - {cls.course.name}"
        raw_data = dao.get_attendance_list(select_class_id, select_date)

        for user, attendance in raw_data:
            absences = dao.count_student_absences(user.id, select_class_id)
            attendance_data.append({
                'user': user,
                'attendance': attendance,
                'absences': absences
            })

    # --- SỬA LỖI TẠI ĐÂY ---
    # Đổi tham số cuối cùng từ 'select_date=select_date' thành 'selected_date=select_date'
    return render_template('GiaoVien_DiemDanh.html',
                           classes=classes,
                           attendance_data=attendance_data,
                           select_class_name=select_class_name,
                           selected_date=select_date)


@app.route('/api/update-grades', methods=['POST'])
@login_required
def update_grades():
    if current_user.role != Role.INSTRUCTOR:
        return jsonify({'error': 'not authorized'}), 403
    data = request.json
    class_id = data.get('class_id')
    grade = data.get('grades')

    if dao.save_grades_list(class_id, grade):
        return jsonify({'msg': 'success'})
    else:
        return jsonify({'error': 'Failed to save grades'}), 500


@app.route('/api/save-attendance', methods=['POST'])
@login_required
def save_attendance_api():
    if current_user.role != Role.INSTRUCTOR:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    class_id = data.get('class_id')
    date_str = data.get('date')
    students = data.get('students')

    try:
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if dao.save_attendance_record(class_id, check_date, students):
            return jsonify({'msg': 'success'})
        else:
            return jsonify({'error': 'Failed to save attendance'}), 500
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400


@app.route('/api/user', methods=['GET'])
def get_user_api():
    if current_user.is_authenticated:
        return jsonify(
            {
                'id': current_user.id,
                'name': current_user.name,
                'username': current_user.username,
                'role': current_user.role.value,
            }
        )
    return jsonify(
        {
            'error': 'Not login'
        }
    )


@app.route('/api/enrollment', methods=['POST'])
def create_enrollment():
    body = request.json
    user_id = int(body.get('user_id'))
    class_id = int(body.get('class_id'))

    enrollment_id = dao.register_course(user_id, class_id)
    if enrollment_id:
        db.session.commit()
        return jsonify({
            'msg': 'success',
            'enrollment_id': enrollment_id
        })
    return jsonify({
        'error': 'Lớp học đã đầy'
    })


@app.route('/api/enrollments', methods=['POST'])
def create_enrollments():
    body = request.json
    user_id = int(body.get('user_id'))
    class_ids = body.get('class_ids', [])

    try:
        with db.session.begin_nested():
            for class_id in class_ids:
                if not dao.register_course(user_id, class_id):
                    raise Exception("class full")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'cannot enroll',
        })
    return jsonify({
        'msg': 'success',
    })


@app.route('/api/enrollment/<int:user_id>/<int:class_id>', methods=['DELETE'])
def delete_enrollment_api(user_id, class_id):
    if not only_current_user(user_id) and current_user.role == Role.STUDENT:
        return jsonify({
            'error': 'permission denied'
        })

    enrollment = dao.get_enrollment(user_id, class_id)
    if enrollment:
        if dao.delete_enrollment(enrollment):
            return jsonify({
                'msg': 'success'
            })
        else:
            return jsonify({
                'error': 'cannot delete enrollment'
            })
    else:
        return jsonify({
            'error': 'enrollment not found'
        })


@app.route('/api/enrollments/<int:user_id>', methods=['GET'])
def get_enrollment_api(user_id):
    no_receipt = request.args.get('no_receipt')
    status = request.args.get('status')
    receipt_id = request.args.get('receipt_id', type=int)
    if no_receipt == 'true':
        enrollments = dao.get_no_receipt_enrollments(user_id)
    elif status:
        enrollments = dao.get_enrollment_receipts_details(user_id, receipt_id, status)
    else:
        enrollments = dao.get_enrollment_by_user(user_id).all()

    enrollment_list = []
    for e, c, course in enrollments:
        enrollment_list.append(
            {
                'id': e.id,
                'course_name': course.name,
                'course_price': course.price,
                'class_name': c.name,
                'course_level': course.level.value,
                'receipt_id': receipt_id if receipt_id else None,
                'class_id': c.id
            }
        )
    return jsonify(enrollment_list)


@app.route('/api/enrollment/<int:enrollment_id>', methods=['GET'])
def get_enrollment_details_api(enrollment_id):
    enrollment = dao.get_enrollment_details_by_id(enrollment_id)
    if enrollment:
        e, c, course = enrollment
        return jsonify(
            {
                'id': e.id,
                'course_name': course.name,
                'course_price': course.price,
                'class_name': c.name,
                'course_level': course.level.value,
                'class_id': c.id
            }
        )
    return jsonify({
        'error': 'enrollment not found'
    })


@app.route('/api/invoice', methods=['POST'])
def create_receipt():
    if current_user.is_authenticated:
        body = request.json
        user_id = body.get('user_id')
        enrollment_ids = body.get('enrollment_ids', [])
        prices = body.get('prices', [])

        receipt = dao.add_receipt(user_id, enrollment_ids, prices)
        if receipt:
            return jsonify({
                'msg': 'success',
                'receipt_id': receipt.id
            })
        else:
            return jsonify({
                'error': 'Đã tạo hoá đơn này rồi'
            })
    return jsonify({
        'error': 'not login'
    })


@app.route('/api/receipts/<int:receipt_id>/status', methods=['PUT'])
def change_receipt_status(receipt_id):
    status = request.json.get('status')
    new_receipt = dao.change_receipt_status(receipt_id, status)
    if new_receipt:
        return jsonify({
            'msg': 'success',
            'receipt_id': new_receipt.id
        })
    else:
        return jsonify({
            'error': 'cannot confirm receipt'
        })


@app.route('/api/send-receipt', methods=['POST'])
def send_receipt():
    body = request.json
    table_html = body.get('table_html')
    user_id = body.get('user_id')
    user = dao.get_user_by_id(user_id)
    try:
        sendEmail(to=user.email,
                  subject='Your Receipt',
                  html_content=table_html)
    except Exception as ex:
        return jsonify({
            'error': 'cannot send email'
        })
    return jsonify({
        'msg': 'success'
    })


@app.route('/api/get-paypal-token', methods=['GET'])
def get_paypal_token():
    token = dao.get_paypal_token()
    if token:
        return jsonify({
            'access_token': token
        })
    else:
        return jsonify({
            'error': 'cannot get token'
        })


@app.route('/api/create-paypal-order', methods=['POST'])
def create_paypal_order():
    token = get_paypal_token()
    if token:
        order_data_json = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': 'USD',
                    'value': '100.00'
                }
            }]
        }
    return None


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    import admin

    app.run(debug=True)
