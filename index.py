import math

from flask import render_template, session, request, url_for
from flask_login import current_user, logout_user, login_user
from werkzeug.utils import redirect

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


@app.route('/login', methods=['POST'])
def login_process():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('home_view'))
    return render_template('index.html')


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
