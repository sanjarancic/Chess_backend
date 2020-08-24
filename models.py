from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy import Enum, ForeignKey

db = SQLAlchemy()


class Match_Type(enum.Enum):
    Friendly = 1
    Random = 2


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_type = db.Column(Enum(Match_Type))
    white_player = db.Column(db.String, ForeignKey('players.username'))
    black_player = db.Column(db.String, ForeignKey('players.username'))
    winner = db.Column(db.String, ForeignKey('players.username'))
    n_moves_white = db.Column(db.Integer)
    n_moves_black = db.Column(db.Integer)
    n_points_white = db.Column(db.Integer)
    n_points_black = db.Column(db.Integer)

    def __init__(self, match_type, white_player):
        self.match_type = match_type
        self.white_player = white_player

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'match_type': 'friendly' if self.match_type == Match_Type.Friendly else 'random',
            'white_player': self.white_player,
            'black_player': self.black_player,
            'winner': self.winner,
            'n_moves_white': self.n_moves_white,
            'n_moves_black': self.n_moves_black,
            'n_points_white': self.n_points_white,
            'n_points_black': self.n_points_black
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Player(db.Model):
    __tablename__ = 'players'
    username = db.Column(db.String, primary_key=True)
    n_points = db.Column(db.Integer, default=0)

    def __init__(self, username):
        self.username = username
        self.n_points = 0

    def __repr__(self):
        return '<username {}>'.format(self.username)

    def serialize(self):
        return {
            'username': self.username,
            'n_points': self.n_points
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
