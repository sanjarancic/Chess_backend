from flask import Flask, request
from config import config
from flask_socketio import SocketIO
from models import Match, Match_Type, db
from sqlalchemy import and_
from flask_socketio import emit
from flask_socketio import join_room
import chess

app = Flask(__name__)

# configuration
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# chess boards
BOARDS = {}


@socketio.on('join_match')
def start_match(data):
    if data['match_type'] == 'friendly':
        # JOIN VIA LINK
        if 'id' in data.keys():
            match = Match.query.filter_by(id=data['id']).first()
            if match and match.black_player is None:
                Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
                join_room(match.id)
                emit('match_started', match.serialize(), room=match.id)
                BOARDS[match.id]['black_player'] = request.sid
            else:
                return emit('invalid_request')
        # SHARE LINK
        else:
            match = Match(Match_Type.Friendly, data['username'])
            match.save()
            emit('match_created', match.serialize())
            join_room(match.id)
            BOARDS[match.id] = {'board': chess.Board(),
                                'white_player': request.sid,
                                'n_moves_white': 0,
                                'n_moves_black': 0}
    else:
        match = Match.query.filter(and_(Match.black_player == None, Match.match_type == Match_Type.Random)).first()
        # FREE SPOT IN A MATCH
        if match:
            Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
            join_room(match.id)
            emit('match_started', match.serialize(), room=match.id)
            BOARDS[match.id]['black_player'] = request.sid

        # ALL SPOTS TAKEN, CREATE NEW MATCH
        else:
            match = Match(Match_Type.Random, data['username'])
            match.save()
            emit('match_created', match.serialize())
            join_room(match.id)
            BOARDS[match.id] = {'board': chess.Board(),
                                'white_player': request.sid,
                                'n_moves_white': 0,
                                'n_moves_black': 0}
    db.session.commit()


@socketio.on('move')
def make_a_move(data):
    if data['id'] not in BOARDS.keys():
        emit('invalid game')
    if data['replace']:
        move = data['from'] + data['to'] + data['replace']
    else:
        move = data['from'] + data['to']

    board = BOARDS[data['id']]['board']
    player = request.sid

    # WHITE PLAYER'S TURN
    if BOARDS[data['id']]['white_player'] == player and board.turn == chess.WHITE and chess.Move.from_uci(
            move) in board.pseudo_legal_moves:
        BOARDS[data['id']]['n_moves_white'] += 1
        board.push(chess.Move.from_uci(move))
        emit('opponent_move', data, room=BOARDS[data['id']]['black_player'])
        if board.is_checkmate():
            match = Match.query.filter_by(id=data['id']).first()
            win = {
                'winner': match.white_player
            }
            print(BOARDS[data['id']])
            Match.query.filter_by(id=match.id).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                              'n_moves_black': BOARDS[data['id']]['n_moves_black'],
                                                              'winner': win['winner']})
            emit('checkmate', win, room=data['id'])
        elif board.is_stalemate():
            Match.query.filter_by(id=data['id']).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                                'n_moves_black': BOARDS[data['id']]['n_moves_black']})
            emit('stealmate', room=data['id'])
        elif board.is_game_over():
            Match.query.filter_by(id=data['id']).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                                'n_moves_black': BOARDS[data['id']]['n_moves_black']})
            emit('game_over', room=data['id'])
        elif board.is_check():
            emit('check', room=data['id'])

    # BLACK PLAYER'S TURN
    elif BOARDS[data['id']]['black_player'] == player and board.turn == chess.BLACK and chess.Move.from_uci(
            move) in board.pseudo_legal_moves:
        BOARDS[data['id']]['n_moves_black'] += 1
        board.push(chess.Move.from_uci(move))
        emit('opponent_move', data, BOARDS[data['id']]['white_player'])
        if board.is_checkmate():
            match = Match.query.filter_by(id=data['id']).first()
            win = {
                'winner': match.black_player
            }
            print(BOARDS[data['id']])
            Match.query.filter_by(id=data['id']).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                              'n_moves_black': BOARDS[data['id']]['n_moves_black'],
                                                              'winner': win['winner']})
            emit('checkmate', win, room=data['id'])
        elif board.is_stalemate():
            Match.query.filter_by(id=data['id']).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                              'n_moves_black': BOARDS[data['id']]['n_moves_black']})
            emit('stealmate', room=data['id'])
        elif board.is_game_over():
            Match.query.filter_by(id=data['id']).update(values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                                                                'n_moves_black': BOARDS[data['id']]['n_moves_black']})
            emit('game_over', room=data['id'])
        elif board.is_check():
            emit('check', room=data['id'])

    else:
        emit('not your move', room=player)
    db.session.commit()

if __name__ == '__main__':
    socketio.run(app)
