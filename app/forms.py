from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectMultipleField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms import widgets

from models import Author, Book


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class BookForm(Form):
    title = TextField('title', validators=[Required()])
    authors = QuerySelectMultipleField('authors', query_factory=lambda:
                Author.query.order_by('name').all(),
                get_label=lambda a: a.name,
                widget=widgets.ListWidget(prefix_label=True),
                option_widget=widgets.CheckboxInput()
    )
class AuthorForm(Form):
    name = TextField('title', validators=[Required()])
    books = QuerySelectMultipleField('books', query_factory=lambda:
                Book.query.order_by('title').all(),
                get_label=lambda b: b.title,
                widget=widgets.ListWidget(prefix_label=True),
                option_widget=widgets.CheckboxInput()
    )
