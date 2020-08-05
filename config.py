import os

POSTGRES = {
    'user': 'chess',
    'pw': 'chess',
    'db': 'chess',
    'host': 'localhost',
    'port': '5432',
}

local_connection = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

connection_string = os.environ['DATABASE_URL'] if 'DATABASE_URL' in os.environ else local_connection


config = {
    'SQLALCHEMY_DATABASE_URI': connection_string,
    'SECRET_KEY': 'secret-key'
}