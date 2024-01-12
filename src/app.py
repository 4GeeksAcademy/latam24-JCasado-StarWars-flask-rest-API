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
from models import db, User, Planets, Characters, FavouritePlanets, FavouriteCharacters

#from models import User

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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response"
    }

    return jsonify(response_body), 200

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("posgres://", "posgresql://")

else: 
    app.config['SQLALCHEMY_DATABASE_URL'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
 
@app.route('/user', methods= ['GET'])
def handle_hello():

    response_body = {
        "msg": "Hi this is your GET /user response"
    }

    return jsonify(response_body), 200


@app.route("/planets", methods= ['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_serialized = list(map(lambda x: x.serialize(), planets))
    return jsonify({"msg": "Completed", "planets": planets_serialized})

@app.route('/planets/<int:planets_id>', methods=['GET'])
def handle_planets(planets_id):
    single_planets = Planets.query.get(planets_id)
    if single_planets is None:
       raise APIException(f"Planet ID not found {planets_id}", status_code=400)
    
    response_body = {
        "msg": "Hello, this is your GET /planets response",
        "planets_id": planets_id,
        "planets_info": single_planets.serialize()
    }

    return jsonify(response_body), 200

@app.route("/characters", methods= ['GET'])
def get_all_characters():
    characters = Characters.query.all()
    characters_serialized = list(map(lambda x: x.serialize(), characters))
    return jsonify({"msg": "Completed", "Characters": characters_serialized})

@app.route('/characters/<int:character_id>', methods=['GET'])
def handle_characters(character_id):
    single_character = Characters.query.get(character_id)
    if single_character is None:
       raise APIException(f"Character ID not found {character_id}", status_code=400)
    
    response_body = {
        "msg": "Hello, this is your GET /characters response",
        "planets_id": character_id,
        "planets_info": single_character.serialize()
    }

    return jsonify(response_body), 200


@app.route("/users", methods= ['GET'])
def get_all_users():
    users = User.query.all()
    users_serialized = list(map(lambda x: x.serialize(), users))
    return jsonify({"msg": "Completed", "users": users_serialized})


@app.route('/users/<int:users_id>', methods=['GET'])
def handle_users(user_id):
    single_user = User.query.get(user_id)
    if single_user is None:
       raise APIException(f"User ID not found {user_id}", status_code=400)
    
    response_body = {
        "msg": "Hello, this is your GET /users response ",
        "users_id": user_id,
        "users_info": single_user.serialize()
    }

    return jsonify(response_body), 200


@app.route('/users/favourites/<int:user_id>', methods= ['GET'])
def user_favourites(user_id):
    
    favourite_planets = FavouritePlanets.query.filter_by(user_id = user_id)  
    Planets = [planets_serialized() for planets in favourite_planets]
    
    favourite_characters = FavouriteCharacters.query.filter_by(user_id = user_id)  
    Characters = [characters_serialized() for characters in favourite_characters]

    return jsonify("Favourite", Planets, Characters ), 200

@app.route('/favourite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    select_planet= Planets.query.get(planet_id)
    body =  request.json
    id_user = body.get("id_user")
    actual_user = User.query.get(id_user)

    FavouritePlanets = FavouritePlanets(
        user = actual_user,
        planets = select_planet
    )

    try:
        db.session.add(FavouritePlanets)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return jsonify({
            "message": "Fatal error",
            "error": error.args
        })
    
    return jsonify({}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
