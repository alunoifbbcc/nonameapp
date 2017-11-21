from flask import url_for, jsonify, g, request
from . import api
from ..models import Comment, Thread
from app import db
from .authentication import auth
from .errors import forbidden

@api.route('/comments/<int:id>/')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())

@api.route('/threads/<int:id>/comments/', methods=['POST'])
@auth.login_required
def new_thread_comment(id):
    thread = Thread.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.thread = thread
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
            {'Location': url_for('api.get_comment', id=comment.id,
                _external=True)}

@api.route('/comments/<int:id>/', methods=['PUT'])
@auth.login_required
def update_comment(id):
    comment = Comment.query.get_or_404(id)
    if g.current_user != comment.author and not \
            g.current_user.is_administrator():
        return forbidden('Insufficient permissions')
    comment.body = request.json.get('body', comment.body)
    db.session.add(comment)
    return jsonify(comment.to_json())
