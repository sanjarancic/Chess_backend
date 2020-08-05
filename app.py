from flask import Flask
from config import config
from flask_socketio import SocketIO
from models import Match, Match_Type, db
from sqlalchemy import and_
from flask_socketio import emit

app = Flask(__name__)

# configuration
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

socketio = SocketIO(app,cors_allowed_origins="*")


@socketio.on('join_match')
def start_match(data):

    if data['match_type'] == 'friendly':
        # JOIN VIA LINK
        if 'id' in data.keys():
            match = Match.query.filter_by(id=data['id']).first()
            if match and match.black_player is None:
                Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
                emit('match_started', match.serialize())
            else:
                return emit('invalid_request')
        # SHARE LINK
        else:
            match = Match(Match_Type.Friendly, data['username'])
            match.save()
            emit('match_created', match.serialize())
    else:
        match = Match.query.filter(and_(Match.black_player == None, Match.match_type == Match_Type.Random)).first()
        # FREE SPOT IN A MATCH
        if match:
            Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
            emit('match_started', match.serialize())
        # ALL SPOTS TAKEN, CREATE NEW MATCH
        else:
            match = Match(Match_Type.Random, data['username'])
            match.save()
            emit('match_created', match.serialize())
    db.session.commit()

if __name__ == '__main__':
    socketio.run(app)
