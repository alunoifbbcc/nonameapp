from flask import jsonify, request, g
from . import api
from ..models import Thread, Topic
from .authentication import auth

@api.route('/threads/<int:id>/')
def get_thread(id):
    thread = Thread.query.get_or_404(id)
    return jsonify(thread.to_json())

@api.route('/topics/<int:id>/threads/', methods=['POST'])
@auth.login_required
def new_topic_thread(id):
    topic = Topic.query.get_or_404(id)
    thread = Thread.from_json(request.json)
    thread.author = g.current_user
    thread.topic = topic
    db.session.add(thread)
    db.session.commit()
    return jsonify(thread.to_json()), 201, \
            {'Location': url_for('api.get_thread', id=thread.id,
                _external=True)}

@api.route('/threads/<int:id>/', methods = ['PUT'])
@auth.login_required
def update_thread(id):
    thread = Thread.query.get_or_404(id)
    if g.current_user != thread.author and not \
            g.current_user.is_administrator():
        return forbidden('Insufficient permissions')
    thread.title = request.json.get('title', thread.title)
    thread.body = request.json.get('body', thread.body)
    db.session.add(thread)
    return jsonify(thread.to_json())
