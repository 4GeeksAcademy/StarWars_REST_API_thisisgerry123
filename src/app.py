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
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# User Endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

# Character Endpoints
@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    return jsonify(character.serialize()), 200

@app.route('/people', methods=['POST'])
def add_person():
    name = request.json.get('name')
    description = request.json.get('description')
    if not name:
        return jsonify({
            "msg": 'Name is required'
        }), 400
    character = Character(name=name, description=description)
    db.session.add(character)
    db.session.commit()
    return jsonify(character.serialize()), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    character.name = request.json.get('name', character.name)
    character.description = request.json.get('description', character.description)
    db.session.commit()
    return jsonify(character.serialize()), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": "Character deleted"}), 200

# Planet Endpoints
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def add_planet():
    name = request.json.get('name')
    description = request.json.get('description')
    if not name:
        return jsonify({
            "msg": 'Name is required'
        }), 400
    planet = Planet(name=name, description=description)
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    planet.name = request.json.get('name', planet.name)
    planet.description = request.json.get('description', planet.description)
    db.session.commit()
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200

# Favorite Endpoints
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = request.json.get('user_id')
    favorite = Favorite(user_id=user_id, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({
            "msg": 'Favorite not found'
        }), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.json.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()
    if favorite is None:
        return jsonify({
            "msg": 'Favorite not found'
        }), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite person deleted"}), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
