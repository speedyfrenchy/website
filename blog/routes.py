from flask import (Flask, abort, flash, Markup, redirect, render_template,
                   request, Response, session, url_for)

from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *
import urllib, functools
from blog import blog, database, flask_db
from .models import Post, FTSPost


@blog.errorhandler(404)
def not_found(exc):
    return render_template('404.html'), 404


@blog.errorhandler(500)
def server_error(exc):
    return render_template('500.html'), 500


@blog.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)


@blog.route('/')
@blog.route('/index')
def index():
    search_query = request.args.get('q')
    if search_query:
        query = Post.search(search_query)
    else:
        query = Post.public().order_by(Post.timestamp.desc())
    return object_list('index.html', query, search=search_query)


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner


@blog.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        if password == blog.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)


@blog.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')


@blog.route('/drafts/')
@login_required
def drafts():
    query = Post.drafts().order_by(Post.timestamp.desc())
    return object_list('index.html', query)


@blog.route('/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Post.select()
    else:
        query = Post.public()
    post = get_object_or_404(query, Post.slug == slug)
    return render_template('detail.html', post=post)


def _create_or_edit(post, template):
    if request.method == 'POST':
        post.title = request.form.get('title') or ''
        post.image = request.form.get('image') or ''
        post.content = request.form.get('content') or ''
        post.published = request.form.get('published') or False
        if not (post.title and post.content):
            flash('Title and Content are required.', 'danger')
        else:
            # Wrap the call to save in a transaction so we can roll it back
            # cleanly in the event of an integrity error.
            try:
                with database.atomic():
                    post.save()
            except IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Post saved successfully.', 'success')
                if post.published:
                    return redirect(url_for('detail', slug=post.slug))
                else:
                    return redirect(url_for('edit', slug=post.slug))

    return render_template(template, post=post)


@blog.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Post(title='', image='', content=''), 'create.html')


@blog.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = get_object_or_404(Post, Post.slug == slug)
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            post.title = request.form['title']
            post.image = request.form['image']
            post.content = request.form['content']
            post.published = request.form.get('published') or False
            post.save()

            flash('Post saved successfully.', 'success')
            if post.published:
                return redirect(url_for('detail', slug=post.slug))
            else:
                return redirect(url_for('edit', slug=post.slug))
        else:
            flash('Title and Content are required.', 'danger')

    return render_template('edit.html', post=post)