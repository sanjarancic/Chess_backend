from flask import Blueprint, request
from models import Match, Match_Type, db
from utils import custom_response
from sqlalchemy import and_

match_api = Blueprint('match_api', __name__)


@match_api.route('/match', methods=['POST'])
def start_match():
    data = request.get_json()

    if data['match_type'] == 'friendly':
        match = Match(Match_Type.Friendly, data['username'])
        match.save()
    else:
        match = Match.query.filter(and_(Match.black_player == None, Match.match_type == Match_Type.Random)).first()
        if match:
            Match.query.filter_by(id=match.id).update(values={'black_player': data['username']})
            match = Match.query.filter_by(id=match.id).first()
        else:
            match = Match(Match_Type.Random, data['username'])
            match.save()
    db.session.commit()
    return custom_response(match.serialize(), 201)

