from datetime import datetime

from flask import flash, request
from flask import url_for, redirect, render_template
from flask_login import current_user, login_user
from flask_login import login_required
from flask_login import logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename

from app import app
from app import db
# noinspection PyUnresolvedReferences
from app import routes, models, errors
from app.forms import EditProfileForm
from app.forms import LoginForm
from app.forms import PostForm
from app.forms import RegistrationForm
from app.models import Post
from app.models import User


class UploadForm(FlaskForm):
    file = FileField()


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save('uploads/' + filename)
        return redirect(url_for('upload'))
    return render_template('static/upload.html', form=form)


@app.route('/test')
def test():
    return render_template("test.html")


@app.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        post.auhtor = current_user.username
        print(current_user.username)
        print(post.auhtor)
        if form.file.data is not None:
            post.image_id = post.unique_id()
            form.file.data.save('app/static/uploads/' + post.image_id + ".jpg")
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('feed'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('feed', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('feed', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('feed.html', title='Лента', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, now=datetime.utcnow().strftime("%d.%m"))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("feed.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Настройки профиля',
                           form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(User.query.all())
        if user is None or not user.check_password(form.password.data):
            return render_template('login.html', title='Вход',
                                   form=form, error="WrongTry")
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Вход', form=form, error="test")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(username=form.username.data,
                            email=form.email.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title="Регистрация", form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc())
    return render_template('user.html', user=user, posts=posts)
