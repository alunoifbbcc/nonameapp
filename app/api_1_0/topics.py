from flask import jsonify, g, url_for, request
from . import api
from ..models import Topic
from .authentication import auth
from app import db

@api.route('/topics/<int:id>/')
def get_topic(id):
    topic = Topic.query.get_or_404(id)
    return jsonify(topic.to_json())

@api.route('/topics/', methods=['POST'])
@auth.login_required
def create_topic():
    topic = Topic.from_json(request.json)
    topic.owner = g.current_user
    db.session.add(topic)
    db.session.commit()
    return jsonify(topic.to_json()), 201, \
            {'Location': url_for('api.get_topic', id=topic.id, _external=True)}

@api.route('/topics/<int:id>/', methods=['PUT'])
@auth.login_required
def update_topic(id):
    topic = Topic.query.get_or_404(id)
    if g.current_user != topic.owner and not \
            g.current_user.is_administrator():
        return forbidden('Insufficient permissions')
    topic.name = request.json.get('name', topic.name)
    topic.description = request.json.get('description', topic.description)
    db.session.add(topic)
    return jsonify(topic.to_json())
