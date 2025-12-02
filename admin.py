from functools import wraps

from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

import dao
from __init__ import app, db
from flask_admin import Admin

from enums import Role
from models import User, Class, Course, Receipt


class BaseModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.ADMIN;

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class UserAdmin(BaseModelView):
    def create_model(self, form):
        model = super().create_model(form)
        model.set_password(form.password_hash.data)
        db.session.commit()
        return model

    form_columns = ['username', 'password_hash', 'role', 'avatar', 'classes']


class ClassAdmin(BaseModelView):
    form_columns = ['name', 'course', 'instructor', 'users', 'max_students']

    form_args = {
        'instructor': {
            'query_factory': lambda: User.query.filter(User.role == Role.INSTRUCTOR).order_by(User.username)
        }
    }


class CourseAdmin(BaseModelView):
    form_columns = ['name', 'description', 'level', 'classes']


admin = Admin(app)
admin.add_view(UserAdmin(User, db.session))
admin.add_view(CourseAdmin(Course, db.session))
admin.add_view(ClassAdmin(Class, db.session))
admin.add_view(ModelView(Receipt, db.session))
