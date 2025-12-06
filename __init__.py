from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cloudinary

twilioRecovery = "MFD4B8DPW6543CAFW9JLKMF6"

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
cloudinary.config(
    cloud_name="dkjmnoilv",
    api_key="564538134111238",
    api_secret="klHdvvFm74zNV7Q0pObFns3PEwE",
    secure=True
)

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Hxjdjdn863@localhost/englishdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PAGE_SIZE"] = 4

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
