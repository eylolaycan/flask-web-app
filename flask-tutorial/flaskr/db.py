import sqlite3

import click
from flask import current_app, g #current app is a special object that points to the Flask application handling the request. Since you used an application factory, there is no application object when writing the rest of your code. g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.

def get_db(): #This function checks if a connection is already stored in the g object. If it is, the connection is returned. If it is not, a new connection is created.
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row #This sets row_factory to make rows behave like dicts. This allows accessing the columns by name.

    return g.db

def close_db(e=None): #This function checks if a connection was created by checking if g.db was set. If the connection exists, it is closed. Further, if this request connected to the database, the connection is closed. If the connection was not created, this function does nothing and the error is ignored.
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db(): #This function opens the schema.sql file, reads the content and executes it against the database.
    db = get_db()

    with current_app.open_resource('schema.sql') as f: #current_app.open_resource() opens a file relative to the flaskr package, which is useful since you won’t necessarily know where that location is when deploying the application later.
        db.executescript(f.read().decode('utf8'))

@click.command('init-db') #This defines a command line command called init-db that calls the init_db function and shows a success message to the user.
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app): #This function takes an application and registers functions with the application instance that are called when the application context is torn down.
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command) #This registers the close_db and init_db_command functions with the application instance.