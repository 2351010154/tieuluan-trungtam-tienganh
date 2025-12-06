import math

import resend
from flask import render_template, session, request, url_for, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.utils import redirect

from dao import get_enrolled_courses_id
from models import Role, only_current_user

import dao
import enums

from __init__ import app, db, login_manager, from_email
from models import User


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
            }
        ],
        Role.CASHIER: [
            {
                'label': 'Lập hoá đơn',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
                'path': '/invoice',
                'url_name': 'invoice_view',
            },
            {
                'label': 'Hoá đơn chờ duyệt',
                'icon_type': 'icon',
                'icon_class': 'lni lni-bookmark-1',
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


@app.context_processor
def sidebar_items():
    return dict(sidebar_items=get_sidebar_items())


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home_view'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login_process():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        home_page = None
        for item in get_sidebar_items():
            if item['url_name']:
                home_page = item['url_name']
                break
        return redirect(url_for(home_page))
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

        r = resend.Emails.send({
            "from": from_email,
            "to": email,
            "subject": "Welcome to Our Platform",
            "html": html_content,
        })
        print(r)

        return redirect(url_for('index'))
    except Exception as ex:
        print(f"Lỗi đăng ký: {str(ex)}")  # In lỗi ra terminal để debug
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
    if current_user.is_authenticated:
        return render_template('invoice.html')
    return redirect(url_for('index'))


@app.route('/receipts')
def receipts_view():
    if current_user.is_authenticated:
        pending_receipts = dao.get_pending_receipts_with_user()
        return render_template('receipts.html', receipts=pending_receipts)
    return redirect(url_for('index'))


@app.route('/admins')
@login_required
def admin_home_view():
    if current_user.is_authenticated:
        return render_template('admin_home.html')
    return redirect(url_for('index'))


@app.route('/admins/baocao')
@login_required
def admin_baocao_view():
    total_records = 50
    per_page = 10
    pages = math.ceil(total_records / per_page)

    current_page = request.args.get('page', 1, type=int)

    return render_template(
        'admin_baocao.html',
        pages=pages,
        current_page=current_page
    )


@app.route('/admins/rules')
def admin_rules_view():
    rules_data = {
        "max_students": 25,
        "tuition_fees": [
            {"id": 1, "name": "Beginner", "price": 1500000},
            {"id": 2, "name": "Intermediate", "price": 2000000},
            {"id": 3, "name": "Advanced", "price": 3500000}
        ]
    }

    return render_template('admin_quydinh.html', rules=rules_data)


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
        return jsonify({'error': 'Course not found'}), 404


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
                'current_size': len(c.users)
            })
        return jsonify(class_list)
    return jsonify({
        'error': 'Classes not found'
    })


@app.route('/giang-vien/bang-diem')
def instructor_home_view():
    return render_template('giaovienindex.html')


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


@app.route('/api/courses/register', methods=['POST'])
def register_course_api():
    body = request.json

    if dao.register_course(body['user_id'], body['class_id']):
        db.session.commit()
        return jsonify({
            'msg': 'success'
        })

    return jsonify({
        'error': 'Lớp học đã đầy'
    })


@app.route('/api/enrollment/<int:user_id>/<int:class_id>', methods=['DELETE'])
def delete_enrollment_api(user_id, class_id):
    if not only_current_user(user_id):
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


@app.route('/api/enrollment/<int:user_id>', methods=['GET'])
def get_enrollment_api(user_id):
    no_receipt = request.args.get('no_receipt')
    status = request.args.get('status')
    receipt_id = request.args.get('receipt_id', type=int)
    enrollment = []
    if no_receipt == 'true':
        enrollment = dao.get_no_receipt_enrollments(user_id)
    elif status:
        enrollment = dao.get_enrollment_receipts_details(user_id, receipt_id, status)
    else:
        enrollment = dao.get_enrollment_by_user(user_id).all()

    print(enrollment)
    enrollment_list = []
    for e, c, course in enrollment:
        enrollment_list.append(
            {
                'id': e.id,
                'course_name': course.name,
                'course_price': course.price,
                'class_name': c.name,
                'course_level': course.level.value,
                'receipt_id': receipt_id if receipt_id else None
            }
        )
    return jsonify(enrollment_list)


@app.route('/api/invoice', methods=['POST'])
def create_receipt():
    if current_user.is_authenticated:
        body = request.json
        user_id = body.get('user_id')
        enrollment_ids = body.get('enrollment_ids', [])
        prices = body.get('prices', [])

        if dao.add_receipt(user_id, enrollment_ids, prices):
            return jsonify({
                'msg': 'success'
            })
        else:
            return jsonify({
                'error': 'Đã tạo hoá đơn này rồi'
            })
    return jsonify({
        'error': 'not login'
    })


@app.route('/api/receipts/<int:receipt_id>/status', methods=['PUT'])
def confirm_receipt(receipt_id):
    if dao.confirm_receipt(receipt_id):
        return jsonify({
            'msg': 'success'
        })
    else:
        return jsonify({
            'error': 'cannot confirm receipt'
        })


@app.route('/api/send-receipt', methods=['POST'])
def get_receipt_table():
    body = request.json
    table_html = body.get('table_html')
    user_id = body.get('user_id')
    user = dao.get_user_by_id(user_id)

    params = {
        "from": from_email,
        "to": user.email,
        "subject": "Your Receipt",
        "html": table_html,
    }
    try:
        r = resend.Emails.send(params)
    except Exception as ex:
        print(ex)
        return jsonify({
            'error': 'cannot send email'
        })
    return jsonify({
        'msg': 'success'
    })


@app.route('/test')
def test_view():
    test = get_enrolled_courses_id(current_user.id)
    print(test)

    return 'Test Page'


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    import admin

    app.run(debug=True)
