from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField, PasswordField
from wtforms.validators import DataRequired
from datetime import datetime

year = datetime.now().year

dates = [i for i in range(year - 100, year)]

types = ['Movie', 'TV show', 'Commercial', 'Establishment', 'Video-Game', 'Toy', 'Celebrity/Public Figure', 'Board-Game', 'Event', 'Other']

class CreatePost(FlaskForm):
    select_year = SelectField('Select best guess at the year your memory is from', choices=dates)
    select_type = SelectField('Select type of nostalgia', choices=types)
    title = StringField('Title This Memory', validators=[DataRequired()])
    description = StringField('Describe Your Memory', render_kw={'class': 'description'}, validators=[DataRequired()])
    submit = SubmitField('Dump')

class SearchForm(FlaskForm):
    search_bar = StringField('search memories', validators=[DataRequired()])
    submit = SubmitField('search')

class CreateAccount(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('create')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login', validators=[DataRequired()])

class Edit(FlaskForm):
    submit = SubmitField('edit', render_kw={'class': 'like-btn', 'style':
        'margin: 0px;' \
        'float:right;' \
        'background: ' \
        'transparent;c' \
        'olor:white;' \
        'border: solid 0px white;' \
        'border-radius: 100%;' \
        'padding-top: 0px;'})

class CommentForm(FlaskForm):
    comment = StringField('comment', validators=[DataRequired()])
    submit = SubmitField('submit', validators=[DataRequired()])


class Delete(FlaskForm):
    submit = SubmitField('delete', render_kw={'class': 'like-btn', 'style':
        'float:right;'
        'background: transparent;'
        'margin: 0px;'
        'color:white;'
        'border: solid 0px white;'
        'border-radius: 100%;'
        'padding-top: 0px;'
        })