from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Membro
class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Etiqueta
class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    color = db.Column(db.String(32))


# Card
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    dueDate = db.Column(db.String(32))
    position = db.Column(db.Integer)
    archived = db.Column(db.Boolean, default=False)
    
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
    labels = db.relationship('Label', secondary='card_label', backref='cards')
    members = db.relationship('Member', secondary='card_member', backref='cards')

# List
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    position = db.Column(db.Integer)
    closed = db.Column(db.Boolean, default=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    cards = db.relationship('Card', backref='list', lazy=True)

# Board
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    background = db.Column(db.String(64))
    visibility = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    lists = db.relationship('List', backref='board', lazy=True)
    members = db.relationship('Member', secondary='board_member', backref='boards')
    labels = db.relationship('Label', secondary='board_label', backref='boards')

board_member = db.Table('board_member',
    db.Column('board_id', db.Integer, db.ForeignKey('board.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'))
)

board_label = db.Table('board_label',
    db.Column('board_id', db.Integer, db.ForeignKey('board.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'))
)

card_label = db.Table('card_label',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'))
)

card_member = db.Table('card_member',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'))
)