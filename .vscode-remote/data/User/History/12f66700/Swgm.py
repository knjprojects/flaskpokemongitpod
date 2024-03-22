import os, csv
import datetime
from flask import Flask, request, redirect, render_template, url_for, flash,jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
    current_user
)
from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=15)
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

# JWT Config to enable current_user
@jwt.user_identity_loader
def user_identity_lookup(user):
  return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)

# *************************************

# Initializer Function to be used in both init command and /init route
# Parse pokemon.csv and populate database and creates user "bob" with password "bobpass"
def initialize_db():
  db.drop_all()
  db.create_all()
  with open('pokemon.csv', newline='', encoding='utf8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if row['height_m'] == '':
        row['height_m'] = None
      if row['weight_kg'] == '':
        row['weight_kg'] = None
      if row['type2'] == '':
        row['type2'] = None

      pokemon = Pokemon(name=row['name'], attack=row['attack'], defense=row['defense'], sp_attack=row['sp_attack'], sp_defense=row['sp_defense'], weight=row['weight_kg'], height=row['height_m'], hp=row['hp'], speed=row['speed'], type1=row['type1'], type2=row['type2'])
      db.session.add(pokemon)
    bob = User(username='bob', email="bob@mail.com", password="bobpass")
    db.session.add(bob)
    db.session.commit()
    bob.catch_pokemon(1, "Benny")
    bob.catch_pokemon(25, "Saul")


def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(
        identity=user
    )  # i changed identity from entire user object to username, now im getting more errors
    return token
  return None

# ********** Routes **************

# Template implementation (don't change)

@app.route('/init')
def init_route():
  initialize_db()
  return redirect(url_for('login_page'))

@app.route("/", methods=['GET'])
def login_page():
  return render_template("login.html")

@app.route("/signup", methods=['GET'])
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods=['POST'])
def signup_action():
  response = None
  try:
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    response = redirect(url_for('home_page',pokemon_id=1))
    token = create_access_token(identity=user)
    set_access_cookies(response, token)
  except IntegrityError:
    flash('Username already exists')
    response = redirect(url_for('signup_page'))
  flash('Account created')
  return response

@app.route("/logout", methods=['GET'])
@jwt_required()
def logout_action():
  response = redirect(url_for('login_page'))
  unset_jwt_cookies(response)
  flash('Logged out')
  return response

# *************************************

# Page Routes (To Update)

def update_list_with_item_at_top(data, clicked_index):
    clicked_item = data.pop(clicked_index)
    data.insert(0, clicked_item)
    return data



@app.route("/app", methods=['GET'])
@app.route("/app/<int:pokemon_id>", methods=['GET'])
@jwt_required()
def home_page(pokemon_id):
    # Fetch all Pokemon data
  all_pokemon = Pokemon.query.all()
  pokemon_data = [pokemon.get_json() for pokemon in all_pokemon]
  """if pokemon_id!=1:
    pokemon_data2= update_list_with_item_at_top(pokemon_data,pokemon_id-1)
  else: pokemon_data2=pokemon_data"""
  mypokes=UserPokemon.query.filter_by(user_id=current_user.id)
  mypokesdata=[pokemon.get_json() for pokemon in mypokes]
  if pokemon_id is not None:
    # Fetch data for a specific Pokemon if an ID is provided
    selected_pokemon = next((pokemon for pokemon in pokemon_data if pokemon['pokemon_id'] == pokemon_id), None)
    if selected_pokemon:
      return render_template("home.html",  all_pokemon=pokemon_data,poke=pokemon_id,mypokes=mypokesdata)
  selected_pokemon=pokemon_data[0]
  return render_template("home.html", all_pokemon=pokemon_data,poke=pokemon_id,mypokes=mypokesdata)
# Action Routes (To Update)

"""@app.route('/login', methods=['POST'])
def login_action():
  response = redirect(url_for('login_page'))
  try:
    data = request.form

    token = login_user(data['username'], data['password'])
    #token = create_access_token(identity=user)
    
    if token:
      flash('Logged in successfully.')  # send message to next page
      response = redirect(url_for('home_page'))
    #response = redirect(url_for('login_page'))  # redirect to main page if login successful
      set_access_cookies(response, token)
  except IntegrityError:
    flash('Invalid username or password')  # send message to next page
    #response = redirect(url_for('login_page'))
  return response"""
@app.route('/login', methods=['POST'])
def login_action():
  response = redirect(url_for('login_page'))
  try:
      data = request.form

      token = login_user(data['username'], data['password'])
      
      if token:
          flash('Logged in successfully.')
          response = redirect(url_for('home_page',pokemon_id=1))
          set_access_cookies(response, token)
      else:
          flash('Invalid username or password')  # Flash message for invalid credentials
  except IntegrityError:
      flash('User does not exist')  # Flash message for user not found
  return response


@app.route("/pokemon/<int:pokemon_id>", methods=['POST'])
@jwt_required()
def capture_action(pokemon_id):
  data=request.form
  pokename=data['name']
  # implement save newly captured pokemon, show a message then reload page
  pokemon=Pokemon.query.filter_by(id=pokemon_id).first()
  user=User.query.filter_by(username=current_user.username).first()
  poke=user.catch_pokemon(pokemon_id,pokename)
  if poke:
    flash(f'{user.username} have captured a wild {pokemon.name}')
  else :flash(f'You failed to capture the wild {pokemon.name}')
  return redirect(request.referrer)

@app.route("/rename-pokemon/<int:pokemon_id>", methods=['POST'])
@jwt_required()
def rename_action(pokemon_id):
  user=User.query.filter_by(username=current_user.username).first()
  data=request.form
  name=data['name']
  pokemon=UserPokemon.query.filter_by(id=pokemon_id).first()
  id=pokemon.pokemon_id
  caught=user.rename_pokemon()
  flash(f'{pokemon.name} renamed to {name}')
  # implement rename pokemon, show a message then reload page
  return redirect(request.referrer)

@app.route("/release-pokemon/<int:pokemon_id>", methods=['GET'])
@jwt_required()
def release_action(pokemon_id):
  # implement release pokemon, show a message then reload page
  return redirect(request.referrer)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
