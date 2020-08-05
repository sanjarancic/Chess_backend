from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy import Enum

db = SQLAlchemy()


class Match_Type(enum.Enum):
    Friendly = 1
    Random = 2


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_type = db.Column(Enum(Match_Type))
    white_player = db.Column(db.String)
    black_player = db.Column(db.String)
    winner = db.Column(db.String)
    n_moves_white = db.Column(db.Integer)
    n_moves_black = db.Column(db.Integer)

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
            'n_moves_black': self.n_moves_black
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
