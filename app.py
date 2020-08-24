from flask import Flask, request
from config import config
from flask_socketio import SocketIO, emit, join_room
from models import Player, Match, Match_Type, db
from sqlalchemy import and_
import chess
import chess.syzygy

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
    if data['username'] == "" or data['username'] is None:
        emit('empty_username')
    else:
        player = Player.query.filter_by(username=data['username']).first()
        if not player:
            player = Player(data['username'])
            player.save()
        if data['match_type'] == 'friendly':
            # JOIN VIA LINK
            if 'id' in data.keys():
                match = Match.query.filter_by(id=data['id']).first()
                if match and match.black_player is None:
                    enter_black(data, match)
                else:
                    return emit('invalid_request')
            # SHARE LINK
            else:
                create_new_match(data)
        else:
            match = Match.query.filter(and_(Match.black_player == None, Match.match_type == Match_Type.Random)).first()
            # FREE SPOT IN A MATCH
            if match:
                enter_black(data, match)

            # ALL SPOTS TAKEN, CREATE NEW MATCH
            else:
                create_new_match(data)

        db.session.commit()


def create_new_match(data):
    match = Match(Match_Type.Random, data['username'])
    match.save()
    emit('match_created', match.serialize())
    join_room(match.id)
    BOARDS[match.id] = {'board': chess.Board(),
                        'white_player': request.sid,
                        'n_moves_white': 0,
                        'n_moves_black': 0,
                        'n_points_white': 0,
                        'n_points_black': 0}


def enter_black(data, match):
    Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
    join_room(match.id)
    emit('match_started', match.serialize(), room=match.id)
    BOARDS[match.id]['black_player'] = request.sid


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
        match = Match.query.filter_by(id=data['id']).first()
        if board.is_checkmate():
            win = {
                'winner': match.white_player
            }
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match, win['winner'])
            else:
                match_update(data, 1, match, win['winner'])
            emit('checkmate', win, room=data['id'])
        elif board.is_stalemate():
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match)
            else:
                match_update(data, 1, match)
            emit('stealmate', room=data['id'])
        elif board.is_game_over():
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match)
            else:
                match_update(data, 1, match)
            emit('game_over', room=data['id'])
        elif board.is_check():
            emit('check', room=data['id'])

    # BLACK PLAYER'S TURN
    elif BOARDS[data['id']]['black_player'] == player and board.turn == chess.BLACK and chess.Move.from_uci(
            move) in board.pseudo_legal_moves:
        BOARDS[data['id']]['n_moves_black'] += 1
        board.push(chess.Move.from_uci(move))
        emit('opponent_move', data, BOARDS[data['id']]['white_player'])
        match = Match.query.filter_by(id=data['id']).first()
        if board.is_checkmate():
            win = {
                'winner': match.black_player
            }
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match, win['winner'])
            else:
                match_update(data, 1, match, win['winner'])
            emit('checkmate', win, room=data['id'])
        elif board.is_stalemate():
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match)
            else:
                match_update(data, 1, match)
            emit('stealmate', room=data['id'])
        elif board.is_game_over():
            if BOARDS[data['id']]['n_moves_white'] + BOARDS[data['id']]['n_moves_black'] <= 100:
                match_update(data, 2, match)
            else:
                match_update(data, 1, match)
            emit('game_over', room=data['id'])
        elif board.is_check():
            emit('check', room=data['id'])

    else:
        emit('not your move', room=player)
    db.session.commit()

def match_update(data, points, match, winner = None):
    Match.query.filter_by(id=data['id']).update(
        values={'n_moves_white': BOARDS[data['id']]['n_moves_white'],
                'n_moves_black': BOARDS[data['id']]['n_moves_black'],
                'winner': winner,
                'n_points_white': points,
                'n_points_black': -points})
    white_player = Player.query.filter_by(username=match.white_player).first()
    black_player = Player.query.filter_by(username=match.black_player).first()
    if winner == white_player:
        white_player.n_points = Player.n_points + points
        black_player.n_points = Player.n_points - points
    else:
        white_player.n_points = Player.n_points - points
        black_player.n_points = Player.n_points + points


@socketio.on('get_leaderboard')
def get_leaderboard():
    user = request.sid
    responce = []
    leaderboard = Player.query.order_by(Player.n_points.desc()).all()
    for player in leaderboard:
        responce.append(player.serialize())

    emit('leaderboard', responce, room=user)


if __name__ == '__main__':
    socketio.run(app)
