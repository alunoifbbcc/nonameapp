from app.main import main
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.decorators import admin_required, permission_required
from app.models import Permission, Thread, Topic, Comment
from app.main.forms import SearchForm, CreateTopicForm, CreateThreadForm, CommentForm
from app import db
from datetime import datetime, timedelta

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect( url_for('main.feed') )
    return render_template('index.html')

@main.route('/active')
def active():
    topics = Topic.query.filter(Topic.last_update > (datetime.now() - timedelta(days=30))).all();
    return render_template('active.html', topics = topics)

@main.route('/search', methods = ['GET', 'POST'])
def search():
    form =  SearchForm()
    if form.validate_on_submit():
        topics = Topic.query.filter(Topic.description.contains(form.value.data)).all()
        topics += Topic.query.filter(Topic.name.contains(form.value.data)).all()
        return render_template('search.html', form = form, topics = topics)
    topics = Topic.query.all()
    return render_template('search.html', form = form, topics = topics)

@main.route('/subscriptions')
@login_required
def subscriptions():
    return render_template('subscriptions.html', topics = current_user.subscriptions)

@main.route('/subscribe/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def subscribe(id):
    topic = Topic.query.filter_by(id = id).first()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    if current_user.is_subscribed(topic):
        flash('You are already subscribed.')
        return redirect(url_for('main.index'))
    current_user.subscribe(topic)
    return redirect(url_for('main.topic', name = topic.name))

@main.route('/unsubscribe/<int:id>')
@login_required
@permission_required(Permission.FOLLOW)
def unsubscribe(id):
    topic = Topic.query.filter_by(id = id).first()
    if topic is None:
        flash('Invalid topic.')
        return redirect(url_for('main.index'))
    if not current_user.is_subscribed(topic):
        flash('You are already not subscribed.')
        return redirect(url_for('main.index'))
    current_user.unsubscribe(topic)
    return redirect(url_for('main.topic', name = topic.name))

@main.route('/thread/<id>', methods = ['GET', 'POST'])
def thread(id):
    thread = Thread.query.filter_by(id = id).first()
    if thread is None:
        return abort(404)
    form = CommentForm()
    if current_user.is_authenticated and form.validate_on_submit():
        comment = Comment(body = form.body.data, author = current_user, thread = thread)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.thread', id = thread.id))
    comments = thread.comments
    return render_template("thread.html", thread = thread, comments = comments, form = form)

@main.route('/createtopic', methods = ['GET', 'POST'])
@login_required
def createtopic():
    form = CreateTopicForm()
    if form.validate_on_submit():
        topic = Topic.query.filter_by(name = form.name.data).first()
        if topic:
            flash('There is already a topic with this name')
            form.name.value = ''
            return render_template('createtopic.html', form = form)
        topic = Topic(name = form.name.data, description = form.description.data, owner = current_user)
        db.session.add(topic)
        db.session.commit()
        return render_template('topic.html', topic = topic) 
    return render_template('createtopic.html', form = form)

@main.route('/createthread/<int:id>', methods = ['GET', 'POST'])
@login_required
def createthread(id):
    form = CreateThreadForm()
    form.id.data = id
    if form.validate_on_submit():
        topic = Topic.query.filter_by(id = form.id.data).first()
        if not topic:
            flash('Invalide Topic')
            return redirect(url_for('main.index'))
        thread = Thread(title = form.title.data, body = form.description.data, author = current_user, topic = topic)
        db.session.add(thread)
        db.session.commit()
        return redirect(url_for('main.thread', id = thread.id))
    return render_template('createtopic.html', id = id, form = form)

@main.route('/topic/<name>')
def topic(name):
    topic = Topic.query.filter_by(name = name).first()
    if topic is not None:
        threads = topic.threads
        return render_template('topic.html', topic = topic, threads = threads)
    return render_template('topic.html')

@main.route('/feed')
@login_required
def feed():
    topics = current_user.subscriptions
    threads = []
    if topics is not None:
        for topic in topics:
            for thread in topic.threads:
                if thread.last_modified > (datetime.utcnow() - timedelta(days = 30)):
                    threads.append(thread)
        return render_template('feed.html', threads = threads)
    flash('You have no subscriptions.')
    return redirect(url_for('main.index'))

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For moderators!"
