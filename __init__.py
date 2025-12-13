from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cloudinary
import resend

PORT = 3000

endpoint_url = "https://api-m.sandbox.paypal.com"
CLIENT_ID = "AbwznLpigSnfmyZzts50BQk8pnKGTNTSrrZTV3nWXmCIo9XZm-RFvN8P8PeVWwQ2UdhSZGT8qyVElidW"
CLIENT_SECRET = "EAoRLC9dXR01dIUFy0v67FMo8NaPGglEOLHhpJ6mECTia_Q0mvphmkI2Tf73sdw1bCQh5_hOrFMqnufD"

resend.api_key = "re_5JKGrhjL_DJxRtm6uWFMs8r7Sk6fSXkGB"
from_email = "no-reply@resend.dev"

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
