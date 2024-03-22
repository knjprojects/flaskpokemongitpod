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

@app.cli.command('list-mypokemon')
@click.argument('username', default='joshua_aka_rat')
def list_my_pokemon(username):
  user=User.query.filter_by(username=username)
  pokes=UserPokemon.query.filter_by(user_id=user.id)
  mypokesdata=[pokemon.get_json() for pokemon in mypokes]
"""@app.cli.command('list-pokemon')
def list_all_pokemon():
  #tabulate package needs to work with an array of arrays
  data = []
  for pokemon in Pokemon.query.all():
    data.append(
      [
            pokemon.attack,
            pokemon.defense,
            pokemon.height,
            pokemon.hp,
            pokemon.name,
            pokemon.id,
            pokemon.sp_attack,
            pokemon.sp_defense,
            pokemon.speed,
            pokemon.type1,
            pokemon.type2,
            pokemon.weight
        ]
    )
  print(tabulate(data, headers=["Attack", "Defense", "Height", "Hp", "Name", "Pokemon_Id"," SpAttack", "SpDefense", "Speed", "Type1", "Type2", "Weight"]))"""