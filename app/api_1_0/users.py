from flask import jsonify, g
from . import api
from ..models import User, Topic, Permission
from .errors import bad_request
from app.api_1_0.authentication import auth
from ..decorators import permission_required

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

@api.route('/unsubscribe/<int:id>')
@auth.login_required
def api_unsubscribe(id):
    topic = Topic.query.get_or_404(id);
    if not g.current_user.is_subscribed(topic):
        return bad_request('You are already not subscribed.')
    g.current_user.unsubscribe(topic)
    return jsonify({'message': 'unsubscribed'})
