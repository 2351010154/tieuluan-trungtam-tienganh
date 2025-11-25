import math

from flask import render_template, session, request, url_for, jsonify
from flask_login import current_user, logout_user, login_user
from werkzeug.utils import redirect

import dao
import enums

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
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
        level = request.args.get('difficulty')
        kw = request.args.get('keyword')
        page = request.args.get('page', 1, type=int)
        return render_template('courses.html', pages=math.ceil(dao.count_course(level, kw) / app.config["PAGE_SIZE"]),
                               courses=dao.get_courses_filter(level, kw, page)
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
                'max_students': c.max_students
            })
        return jsonify(class_list)
    return jsonify({
        'error': 'Classes not found'
    })


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    import admin

    app.run(debug=True)
