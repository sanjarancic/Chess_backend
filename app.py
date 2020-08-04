from flask import Flask
from config import config
from models import db

app = Flask(__name__)

# configuration
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = config['SECRET_KEY']

db.init_app(app)


if __name__ == '__main__':
    app.run()
