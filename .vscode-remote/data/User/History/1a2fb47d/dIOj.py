import click, sys, csv
from App import app, initialize_db
from tabulate import tabulate
from App import  User, UserPokemon, Pokemon, db

from sqlalchemy.exc import IntegrityError


db.init_app(app)
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  initialize_db()
  print('database initialized')


@app.cli.command('get-users')
def get_users():
  users = User.query.all()
  print(users)
