from . import api
from ..models import User, AnonymousUser
from flask import g, jsonify, current_app, request
from flask_login import current_user
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from .errors import bad_request, unauthorized
from flask_httpauth import HTTPTokenAuth

auth  = HTTPTokenAuth(scheme = 'Bearer')

@auth.verify_token
def verify_token(token):
    g.current_user = AnonymousUser
    jwt = JWT(current_app.config['SECRET_KEY'], expires_in = 3600)
    try:
        data = jwt.loads(token)
    except:
        return False
    if 'id' in data:
        g.current_user = User.query.get(data['id'])
        print(g.current_user)
        if g.current_user is not None:
            return True
    return False

@api.route('/login/', methods = ['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        return bad_request('Missing one or more key-value pair')
    #(TODO) Maybe this is a unnecessary test
    if email == '' or password == '':
        return bad_request('Invalid parameters')
    user = User.query.filter_by(email = email).first()
    if user is None:
        #(TODO)Needs a more descriptive message
        return bad_request('Invalid credentials')
    #(TODO)Decrypt the password field (Base64 or something else)
    if user.verify_password(password):
        g.current_user = user
        token = g.current_user.generate_auth_token(expiration=3600).decode('ascii')
        print(token)
        return jsonify({'token': token, 'expiration': 3600, 'id' : g.current_user.id}), 200
    return bad_request('Invalid credentials')
