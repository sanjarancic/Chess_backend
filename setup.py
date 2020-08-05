from setuptools import setup

dependencies = [
    'flask',
    'flask_migrate',
    'flask_script',
    'flask_sqlalchemy',
    'sqlalchemy',
    'psycopg2',
    'flask_socketio',
    'flask_cors',
    'gunicorn'
]

setup(
    name="Chess_backend",
    version="1.0",
    author="Sanja Rancic",
    install_requires=dependencies
)