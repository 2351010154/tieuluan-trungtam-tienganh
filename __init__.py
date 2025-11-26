from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

CLOUDINARY_URL = "CLOUDINARY_URL=cloudinary://564538134111238:klHdvvFm74zNV7Q0pObFns3PEwE@dkjmnoilv"
CLOUDINARY_KEY = "564538134111238"
CLOUDINARY_SECRET = "klHdvvFm74zNV7Q0pObFns3PEwE"

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:120505Hh@localhost/englishdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PAGE_SIZE"] = 4

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
