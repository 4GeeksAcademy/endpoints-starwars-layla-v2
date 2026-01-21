from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    people_favorites = relationship("People", secondary="user_people_favorite")

    planet_favorites = relationship("Planets", secondary="user_planet_favorite")

    @property
    def favorites(self):
        all_favorites = self.people_favorites + self.planet_favorites
        return all_favorites

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
    
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=False, nullable=False)
    height = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.String(10), nullable=True)
    gender = db.Column(db.String(10), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "weight": self.weight,
            "gender": self.gender
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    climate = db.Column(db.String(10), nullable=True)
    terrain = db.Column(db.String(10), nullable=True)
    resources = db.Column(db.String(10), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "resources": self.resources
        }

    
class UserPeopleFavorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), primary_key=True)

    def serialize(self):
        return {
            "user_id": self.user_id,
            "people_id": self.people_id
        }

class UserPlanetFavorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), primary_key=True)

    def serialize(self):
        return {
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }