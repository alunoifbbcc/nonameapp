from flask import jsonify
from . import api
from ..models import User

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/subscriptions/')
def get_user_subscriptions(id):
    user = User.query.get_or_404(id)
    return jsonify({'subscriptions' :
        [subscription.to_json() for subscription in user.subscriptions]})

@api.route('/users/<int:id>/topics/')
def get_user_topics(id):
    user = User.query.get_or_404(id)
    return jsonify({'topics' : [topic.to_json() for topic in user.topics]})

@api.route('/users/<int:id>/thread/')
def get_user_threads(id):
    user = User.query.get_or_404(id)
    return jsonify({'threads' : [thread.to_json() for thread in user.threads]})
