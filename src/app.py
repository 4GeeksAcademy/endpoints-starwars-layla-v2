"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, UserPeopleFavorite, UserPlanetFavorite
from sqlalchemy import select

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# GET USERS


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# GET PEOPLE


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    serialized_people_list = list(map(lambda x: x.serialize(), people))
    return jsonify(serialized_people_list), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify(person.serialize()), 200

# POST PEOPLE


@app.route('/people', methods=['POST'])
def add_person():
    request_body = request.get_json()
    person = People(name=request_body["name"], height=request_body["height"],
                    weight=request_body["weight"], gender=request_body["gender"])
    db.session.add(person)
    db.session.commit()
    return f"The person {request_body['name']} was added to the database", 200

# GET PLANETS


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    serialized_planets_list = list(map(lambda x: x.serialize(), planets))
    return jsonify(serialized_planets_list), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200

# POST PLANETS


@app.route('/planets', methods=['POST'])
def add_planet():
    request_body = request.get_json()
    planet = Planets(name=request_body["name"], climate=request_body["climate"],
                     terrain=request_body["terrain"], resources=request_body.get("resources"))
    db.session.add(planet)
    db.session.commit()
    return f"The planet {request_body['name']} was added to the database", 200

# GET FAVORITOS 1


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')

    if user_id is None:
        return jsonify({"error": "User ID is required."}), 400

    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found."}), 404

    people_favorites = UserPeopleFavorite.query.filter_by(
        user_id=user_id).all()
    people_list = []
    for fav in people_favorites:
        person = People.query.get(fav.people_id)
        if person:
            people_list.append({
                "type": "people",
                "id": person.id,
                "name": person.name
            })

    planet_favorites = UserPlanetFavorite.query.filter_by(
        user_id=user_id).all()
    planet_list = []
    for fav in planet_favorites:
        planet = Planets.query.get(fav.planet_id)
        if planet:
            planet_list.append({
                "type": "planet",
                "id": planet.id,
                "name": planet.name
            })

    return jsonify({
        "user_id": user_id,
        "people_favorites": people_list,
        "planet_favorites": planet_list
    }), 200

# POST AGREGAR FAVORITO PEOPLE


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get('user_id')

    if user_id is None:
        return jsonify({"error": "User ID is required."}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404

    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found."}), 404

    existing_favorite = UserPeopleFavorite.query.filter_by(
        user_id=user_id,
        people_id=people_id
    ).first()

    if existing_favorite:
        return jsonify({"error": "This person is already in favorites."}), 400

    favorite_relation = UserPeopleFavorite(
        user_id=user_id, people_id=people_id)
    db.session.add(favorite_relation)
    db.session.commit()

    return jsonify({"message": f"Added {person.name} to favorites for user {user.name}"}), 200

# POST AGREGAR FAVORITO PLANET


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')

    if user_id is None:
        return jsonify({"error": "User ID is required."}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404

    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found."}), 404

    existing_favorite = UserPlanetFavorite.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    if existing_favorite:
        return jsonify({"error": "This planet is already in favorites."}), 400

    favorite_relation = UserPlanetFavorite(
        user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_relation)
    db.session.commit()

    return jsonify({"message": f"Added {planet.name} to favorites for user {user.name}"}), 200

# DELETE FAVORITO PEOPLE


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.json.get('user_id')

    if user_id is None:
        return jsonify({"error": "User ID is required."}), 400

    favorite_relation = UserPeopleFavorite.query.filter_by(
        user_id=user_id,
        people_id=people_id
    ).first()

    if favorite_relation is None:
        return jsonify({"error": "Favorite not found."}), 404

    person = People.query.get(people_id)
    person_name = person.name if person else "Unknown"

    db.session.delete(favorite_relation)
    db.session.commit()

    return jsonify({"message": f"Favorite person {person_name} deleted successfully"}), 200

# DELETE FAVORITO PLANET


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')

    if user_id is None:
        return jsonify({"error": "User ID is required."}), 400

    favorite_relation = UserPlanetFavorite.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    if favorite_relation is None:
        return jsonify({"error": "Favorite not found."}), 404

    planet = Planets.query.get(planet_id)
    planet_name = planet.name if planet else "Unknown"

    db.session.delete(favorite_relation)
    db.session.commit()

    return jsonify({"message": f"Favorite planet {planet_name} deleted successfully"}), 200

# ENDPOINT ESPECIAL FACUNDO


@app.route("/user-favorite-people", methods=["GET"])
def get_all_user_favorite_people():
    ufps = db.session.execute(select(UserPeopleFavorite)).scalars().all()
    return jsonify({"user-favorite-people": [ufp.serialize() for ufp in ufps]}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
