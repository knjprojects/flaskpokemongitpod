import click
from App import app, initialize_db
import click, sys, csv
from tabulate import tabulate
from models import db, Todo, Admin, RegularUser, db, User
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
