from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy import Enum

db = SQLAlchemy()

class MyEnum(enum.Enum):
    Friendly = 1
    Random = 2

class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_type = db.Column(Enum(MyEnum))
    white_player = db.Column(db.String)
    black_player = db.Column(db.String)
    winner = db.Column(db.String)
    n_moves_white = db.Column(db.Integer)
    n_moves_black = db.Column(db.Integer)

    def __init__(self, white_player, black_player, winner, n_moves_white, n_moves_black):
        self.white_player = white_player
        self.black_player = black_player
        self.winner = winner
        self.n_moves_white = n_moves_white
        self.n_moves_black = n_moves_black

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,

            'white_player': self.white_player,
            'black_player': self.black_player,
            'winner': self.winner,
            'n_moves_white': self.n_moves_white,
            'n_moves_black': self.n_moves_black
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

