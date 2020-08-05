from flask import Response
import json


def custom_response(message_obj, status_code=200):
    return Response(
        mimetype="application/json",
        response=json.dumps(message_obj),
        status=status_code
    )
