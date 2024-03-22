import click, sys, csv
from App import app, initialize_db
from tabulate import tabulate
from App import db, User, Pokemon, UserPokemon
from sqlalchemy.exc import IntegrityError


#db.init_app(app)
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  initialize_db()
  print('database initialized')


@app.cli.command('get-users')
def get_users():
  users = User.query.all()
  print(users)
  
@app.cli.command('list-pokemon')
def get_pokemons():
  pokemon = Pokemon.query.all()
  print(pokemon)
