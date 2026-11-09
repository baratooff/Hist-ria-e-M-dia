from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config["SECRET_KEY"] = "24533a4d1e0c46d2b3d667f27ccb3971a564a608"
if os.getenv("DATABASE_URL"):
    uri = os.getenv("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///PFC.db"


bcrypt = Bcrypt(app)
database = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "alert-info"

from PFC import routes
