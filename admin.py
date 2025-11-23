from flask_admin.contrib.sqla import ModelView

from __init__ import app, db
from flask_admin import Admin

from models import User, Class, Course


class UserAdmin(ModelView):
    def create_model(self, form):
        model = super().create_model(form)
        model.set_password(form.password_hash.data)
        db.session.commit()
        return model

    form_columns = ['username', 'password_hash', 'role', 'avatar', 'classes']


class ClassAdmin(ModelView):
    form_columns = ['name', 'course', 'users', 'max_students']


admin = Admin(app)
admin.add_view(UserAdmin(User, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ClassAdmin(Class, db.session))
