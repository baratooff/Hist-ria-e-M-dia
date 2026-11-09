from PFC import app, database
from PFC.models import Usuario, Post

with app.app_context():
    database.create_all()
