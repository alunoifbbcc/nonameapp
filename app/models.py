from app import db, login_manager
from werkzeug.security import generate_password_hash, \
        check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from sqlalchemy import event, DDL

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    POST = 0x04
    MODERATE = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.POST, True),
            'Moderator': (Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.POST |
                    Permission.MODERATE, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

topic_mod = db.Table('topic_mod', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('topic_id', db.Integer, db.ForeignKey('topics.id')))

subscription = db.Table('subscriptions', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('topic_id', db.Integer, db.ForeignKey('topics.id')))



class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default = False)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)

    topic = db.relationship('Topic', backref='owner', lazy = 'dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    threads = db.relationship('Thread', backref = 'author', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'author', lazy = 'dynamic')
    """
    subscriptions = db.relationship('Topic', 
            secondary = subscription,
            backref = db.backref('subscribers', lazy = 'dynamic'), lazy='dynamic')
    """
    subscriptions = db.relationship('Topic', secondary = subscription,
            backref = db.backref('subscribers', lazy = 'dynamic'), lazy = 'dynamic')

    moderates = db.relationship('Topic', 
            secondary = topic_mod,
            backref = db.backref('moderators', lazy = 'dynamic'), lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_subscribed(self, topic):
        return topic in self.subscriptions

    def subscribe(self, topic):
        if not self.is_subscribed(topic):
            self.subscriptions.append(topic)
            db.session.commit()

    def unsubscribe(self, topic):
        if self.is_subscribed(topic):
            #topic.subscribers.remove(self)
            self.subscriptions.remove(topic)
            #db.session.add(self.subscriptions)
            db.session.commit()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()
            #if self.email == current_app.config['NONAME_ADMIN']:
            #    self.role = Role.query.filter_by(permissions = 0xff).first()
            
    def __repr__(self):
        return '<User %r>' % self.username

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    threads = db.relationship('Thread', backref='topic', lazy = 'dynamic')

    def __repr__(self):
        return '<Topic %r>' % self.name

class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(512))
    body = db.Column(db.Text)
    last_modified = db.Column(db.DateTime(), default=datetime.utcnow)
    creation_date = db.Column(db.DateTime(), default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))

    comments = db.relationship('Comment', backref='thread', lazy = 'dynamic')

    def __repr__(self):
        return '<Topic %r>' % self.title

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'))

    def __repr__(self):
        return '<Post %r>' % self.body


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_subscribed(self, topic):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
