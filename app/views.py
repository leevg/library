from flask import render_template, flash, redirect,\
    session, url_for, request, g
from flask.ext.login import login_user, logout_user,\
    current_user, login_required

from app import app, db, lm, oid

from forms import LoginForm, AuthorForm, BookForm

from models import User, ROLE_USER, Book, Author


@lm.user_loader
def load_user(id):
    '''Load user by given id.'''
    return User.query.get(int(id))


@app.before_request
def before_request():
    '''Setup global user.'''
    g.user = current_user
    

@app.route('/')
@app.route('/index')
def index():
    '''Render index page.'''
    user = g.user
    return render_template('index.html', title='Library', user=user)


@app.route('/books')
def books():
    '''Render page with books.'''
    books = Book.query.order_by(Book.title)
    return render_template('books.html', books=books)


@app.route('/book/<id>')
def book(id):
    '''Render book info by gicen id or 404 if book doesn't exist'''
    book = Book.query.filter_by(id=id).first_or_404()
    return render_template('book.html', book=book)


@app.route('/delete_book/<id>')
@login_required
def delete_book(id):
    '''Delete book by given id.'''
    book = Book.query.filter_by(id=id).first_or_404()
    db.session.delete(book)
    db.session.commit()
    flash('Book was successfully deleted')
    return redirect(url_for('books'))


@app.route('/edit_book/<id>', methods=['GET', 'POST'])
@app.route('/add_book/<id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    '''Editing or adding new book depends on given id.'''
    if id == 'new':
        book = Book()
    else:
        book = Book.query.filter_by(id=id).first_or_404()
    form = BookForm(request.form, obj=book)
    if request.method == 'GET':
        return render_template('edit_book.html', form=form)
    if request.method == 'POST' and form.validate():
        form.populate_obj(book)
        book.title = form.title.data
        book.authors = form.authors.data
        if id == 'new':
            db.session.add(book)
            flash('Book was successfully added')
        else:
            db.session.merge(book)
            flash('Book was successfully updated')
        db.session.commit()
        return redirect(url_for('book', id=book.id))
    else:
        return render_template('edit_book.html', form=form)


@app.route('/authors')
def authors():
    '''Render page with authors.'''
    authors = Author.query.order_by(Author.name)
    return render_template('authors.html', authors=authors)


@app.route('/author/<id>')
def author(id):
    '''Render page with author info by id or 404 if author doesn't exist.'''
    author = Author.query.filter_by(id=id).first_or_404()
    return render_template('author.html', author=author)


@app.route('/delete_author/<id>')
@login_required
def delete_author(id):
    '''Delete author by given id or 404 if doesn't exist'''
    author = Author.query.filter_by(id=id).first_or_404()
    db.session.delete(author)
    db.session.commit()
    flash('Author was successfully deleted')
    return redirect(url_for('authors'))


@app.route('/edit_author/<id>', methods=['GET', 'POST'])
@app.route('/add_author/<id>', methods=['GET', 'POST'])
@login_required
def edit_author(id):
    '''Editing or adding author depending on given id.'''
    if id == 'new':
        author = Author()
    else:
        author = Author.query.filter_by(id=id).first_or_404()
    form = AuthorForm(request.form, obj=author)
    if request.method == 'GET':
        return render_template('edit_author.html', form=form)
    if request.method == 'POST' and form.validate():
        form.populate_obj(author)
        author.name = form.name.data
        author.books = form.books.data
        if id == 'new':
            db.session.add(author)
            flash('Author was successfully added')
        else:
            db.session.merge(author)
            flash('Author info was successfully updated')
        db.session.commit()
        return redirect(url_for('author', id=author.id))
    else:
        return render_template('edit_author.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    '''Render login page or redirect to index if authenticated'''
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', title='Sign In', form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    '''Allow to requested page if authenticated or redirect to login page.'''
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    '''Logout from the system.'''
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
