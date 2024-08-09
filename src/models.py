from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password_hash = db.Column(db.String(250), nullable=False)
    favorites = db.relationship("Favorite", backref="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": [favorite.serialize() for favorite in self.favorites]
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    favorites = db.relationship("Favorite", backref="character")

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    favorites = db.relationship("Favorite", backref="planet")

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)

    def __init__(self, user_id, character_id=None, planet_id=None):
        self.user_id = user_id
        self.character_id = character_id
        self.planet_id = planet_id
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "date": self.date.isoformat()
        }