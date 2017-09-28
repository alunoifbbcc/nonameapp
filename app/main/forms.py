from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, HiddenField
from wtforms.validators import Required, Length, Regexp, EqualTo
from app.models import User

class SearchForm(FlaskForm):
    value = StringField('',validators = [Required(), Length(3, 64)])
    submit = SubmitField('Search')

class CreateTopicForm(FlaskForm):
    name = StringField('Name', validators = [Required(), Length(3, 64)])
    description = TextField('Description', validators = [Required()])
    submit = SubmitField('Create')

class CreateThreadForm(FlaskForm):
    id = HiddenField()
    title = StringField('Title', validators = [Required(), Length(3, 64)])
    description = TextField('Description', validators = [Required()])
    submit = SubmitField('Create')

class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')
