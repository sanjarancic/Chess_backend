POSTGRES = {
    'user': 'chess',
    'pw': 'chess',
    'db': 'chess',
    'host': 'localhost',
    'port': '5432',
}

config = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES,
    'SECRET_KEY': 'secret-key'
}