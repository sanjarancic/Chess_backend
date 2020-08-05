from flask import Flask
from config import config
from models import db
from routes.match import match_api
from flask_socketio import SocketIO

app = Flask(__name__)
app.register_blueprint(match_api)

# configuration
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)

db.init_app(app)


if __name__ == '__main__':
    socketio.run(app)

