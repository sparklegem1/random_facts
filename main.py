from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_bootstrap import Bootstrap
from functools import wraps
from forms import *
from flask_sqlalchemy import SQLAlchemy
import re
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memory_dump.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "12345"
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

now = datetime.now()

# USER OBJECT
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    #RELTIONSHIPS
    memory = relationship('MemoryData', back_populates='user')
    comments = relationship('Comment', back_populates='user')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

db.create_all()

# MEMORY OBJECT
class MemoryData(db.Model):
    __tablename__ = 'memories'
    __searchable__ = ['year', 'type', 'title', 'description', 'created']
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    created = db.Column(db.String(12), nullable=False)
    likes = db.Column(db.Integer, nullable=True)

    # RELATIONSHIPS
    # PARENT
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='memory')

    #CHILDREN
    comments = relationship('Comment', back_populates='memory')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

db.create_all()

# COMMENT
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.String(10))

    # USER PARENT
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='comments')

    # MEMORY PARENT
    memory_id = db.Column(db.Integer, db.ForeignKey('memories.id'))
    memory = relationship('MemoryData', back_populates='comments')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

db.create_all()

# SEARCH ALGORITHM
def find_all_words(words, sentence):

    search_words = re.findall(r'\w+', words)
    search_words_lower = []
    search_words_upper = []
    for word in search_words:
        search_words_lower.append(word.lower())
        search_words_upper.append(word.upper())

    sentence_words = re.findall(r'\w+', sentence)
    sentence_words_lower = []
    sentence_words_upper = []
    for word in sentence_words:
        sentence_words_lower.append(word.lower())
        sentence_words_upper.append(word.upper())

    words_found = 0
    for word in search_words:
        if word in sentence_words:
            words_found += 1
    for word in search_words_upper:
        if word in sentence_words_upper:
            words_found += 1
    for word in search_words_lower:
        if word in sentence_words_lower:
            words_found += 1
    return words_found

# ADMIN ONLY
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if current_user.id != 1:
                return abort(403)
        except AttributeError:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# HOME
@app.route('/')
def home():
    return render_template('index.html', year=datetime.now().year) # year is for footer



# MAIN-PAGE
@app.route('/main-page', methods=['GET', 'POST'])
def main_page():
    memories = MemoryData.query.all()
    results = []
    form = SearchForm()
    if form.validate_on_submit():
        for obj in memories:
            if find_all_words(obj.year, form.search_bar.data) != 0 or find_all_words(obj.type, form.search_bar.data) != 0 or find_all_words(obj.title, form.search_bar.data) != 0 or find_all_words(obj.description, form.search_bar.data) != 0:
                results.append(obj)
        return render_template('main-page.html', memories=results, form=form, year=datetime.now().year) # year is still for footer
    return render_template('main-page.html', memories=memories, form=form, year=datetime.now().year)

# CREATE-ACCOUNT
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = CreateAccount()
    if form.validate_on_submit():
        password = form.password.data
        to_hash = password
        hash = generate_password_hash(to_hash, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hash
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('main_page'))
    return render_template('create-account.html', form=form, year=datetime.now().year)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        password = form.password.data
        if not user:
            flash('No user with that email')
            return redirect(url_for('login'))
        if user and not check_password_hash(user.password, password):
            flash('Password is incorrect')
            return redirect(url_for('login'))
        if user and check_password_hash(user.password, password):
            if user.id == 1:
                admin = True
                print(admin)
                login_user(user)
                return redirect(url_for('main_page', admin=admin))
            else:
                login_user(user)
                return redirect(url_for('main_page'))
    return render_template('login.html', form=form, year=datetime.now().year)

# CREATE DUMP
@app.route('/create-dump', methods=['GET', 'POST'])
def create_dump():
    form = CreatePost()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must first login to make a review')
            return redirect(url_for('login'))
        memory = MemoryData(
            year=form.select_year.data,
            type=form.select_type.data,
            title=form.title.data,
            description=form.description.data,
            created=str(datetime.now())[:11],
            user_id=current_user.id,
            likes=0
        )
        db.session.add(memory)
        db.session.commit()
        return redirect(url_for('main_page'))
    return render_template('create-post-form.html', form=form, year=datetime.now().year)

#COMMENTS PAGE
@app.route('/comments/<int:id>', methods=['GET', 'POST'])
def comments(id):
    memory = MemoryData.query.get(id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            comment=form.comment.data,
            user_id=current_user.id,
            created=str(datetime.now())[:11],
            memory_id=memory.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return render_template('comment.html', memory=memory, form=form, year=datetime.now().year)
    return render_template('comment.html', memory=memory, form=form, year=datetime.now().year)

#EDIT MEMORY PAGE
@app.route('/edit-memory/<int:id>', methods=['GET', 'POST'])
def edit_memory(id):
    memory = MemoryData.query.get(id)
    form = CreatePost(
        select_year=memory.year,
        select_type=memory.type,
        title=memory.title,
        description=memory.description
    )
    if form.validate_on_submit():
        if memory.user.id == current_user.id:
            memory.type = form.select_type.data
            memory.year = form.select_year.data
            memory.title = form.title.data
            memory.description = form.description.data
            db.session.commit()
            return redirect(url_for('main_page'))
        else:
            return 'this is not your post to edit'
    return render_template('create-post-form.html', form=form, year=datetime.now().year)

# LOGOUT
@app.route('/log-out')
def logout():
    logout_user()
    return redirect(url_for('home'))


############################ API #############################


@app.route('/api/get-all-memories')
def get_all_memories():
    memories = MemoryData.query.all()
    memory_dict = {memory.to_dict() for memory in memories}
    return jsonify(memory_dict)

@app.route('/api/query-memories/<query>')
def query_memories(query):
    memories = MemoryData.query.all()
    results = []
    for mem in memories:
        data = mem.to_dict()
        for k in data:
            if find_all_words(str(data[k]), query) != 0:
                results.append(data)
                break
    return jsonify(results)

@app.route('/api/get-all-user-memories/<username>/<password>')
def get_user_memories(username, password):
    user = User.query.filter_by(username=username).first()
    memories = {'memories': []}
    if user and check_password_hash(user.password, password):
        user_memories = MemoryData.query.filter_by(user_id=user.id).all()
        for memory in user_memories:
            memories['memories'].append(memory.to_dict())
        return jsonify(memories)
    else:
        return jsonify({'message': 'incorrect credentials'})

@app.route('/api/get-all-usernames')
def get_all_usernames():
    users = User.query.all()
    usernames = [user.to_dict()['username'] for user in users]
    return jsonify({'usernames': usernames})

@app.route('/api/query-users/<query>')
def query_users(query):
    users = User.query.all()
    usernames = [user.username for user in users]
    if query in usernames:
        return jsonify({query: 'this user exists'})
    else:
        return jsonify({'message': 'this user does not exist'})

@app.route('/api/edit-memory/<username>/<password>/<title>/<attr>/<change>', methods=['GET', 'POST'])
def api_edit_memory(username, title, password, attr, change):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        memory = MemoryData.query.filter_by(title=title).first()
        if memory:
            if memory.user.id == user.id:
                getattr(memory, attr)
                db.session.commit()
                return jsonify(memory.to_dict())
            else:
                return jsonify({'message': 'you are not authorized to edit this memory'})
        else:
            return jsonify({'message': 'failure'})
    else:
        return jsonify({'message': 'incorrect credentials'})

@app.route('/api/delete-memory/<username>/<password>/<title>', methods=['GET', 'DELETE'])
def api_delete_memory(username, password, title):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        memory = MemoryData.query.filter_by(title=title).first()
        if memory.user.id == user.id:
            db.session.delete(memory)
            db.session.commit()
            return jsonify({'message':'success'})
        else:
            return jsonify({'message': 'failure'})
    else:
        return jsonify({'message': 'incorrect credentials'})






"""
//TODO: Add likes to post obj
//TODO: Add users
//TODO: Add sessions
//TODO: edit navbar when logged in
//TODO: logout 
//TODO: make api
//TODO: make commetns page
TODO: set up git 
TODO: deploy

"""


if __name__ == '__main__':
    app.run(debug=True)