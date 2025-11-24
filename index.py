import math

from flask import render_template, session, request, url_for
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.utils import redirect
from models import Role

import dao
import enums
from admin import admin

from __init__ import app, db, login_manager
from models import User


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home_view'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_process():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)

        if user.role == Role.ADMIN:
            return redirect(url_for('admin_home_view'))
        elif user.role == Role.STUDENT:
            return redirect(url_for('home_view'))

    return render_template('index.html', err_mgs='Sai mật khẩu hoặc tài khoản')

@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_process():
    password = request.form['password']
    confirm = request.form['confirm']

    if password != confirm:
        err_msg = 'Mật Khẩu Không Khớp!'
        return render_template('register.html', err_msg=err_msg)
    avatar = request.files['avatar']

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/home')
def home_view():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_home_view():
    if current_user.is_authenticated:
        return render_template('admin_home.html')
    return redirect(url_for('index'))

@app.route('/admin/baocao')
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

@app.route('/admin/rules')
def admin_rules_view():
    rules_data = {
        "max_students": 25,
        "tuition_fees": [
            {"id": 1, "name": "Beginner", "price": 1500000},
            {"id": 2, "name": "Intermediate", "price": 2000000},
            {"id": 3, "name": "Advanced", "price": 3500000}
        ]
    }

    return render_template(
        'admin_quydinh.html',
        rules=rules_data
    )

@app.route('/courses')
def courses_view():
    level = request.args.get('difficulty')
    kw = request.args.get('keyword')
    page = request.args.get('page', 1, type=int)

    return render_template('courses.html', pages=math.ceil(dao.count_course(level, kw) / app.config["PAGE_SIZE"]),
                           courses=dao.get_courses_filter(level, kw, page)
                           , levels=enums.Level)


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
