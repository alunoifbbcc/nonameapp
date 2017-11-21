from flask import jsonify
from app.exceptions import ValidationError
from . import api

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response

def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def not_found():
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response

def internal_server_error():
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
