"""
Database configuration for a Flask instance
"""
import binascii
import os

# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = binascii.hexlify(os.urandom(24))

DATA_BACKEND = 'cloudsql'
PROJECT_ID = 'various-plans'

# CloudSQL / SQLAlchemy configuration
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'various-plans-sql'
CLOUDSQL_DATABASE = 'vplans_db'
CLOUDSQL_CONNECTION_NAME = 'various-plans:europe-west1:library'

LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE)

LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+mysqldb://{user}:{password}@/{database}?unix_socket=/cloudsql/{connection_name}').format(
        user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD,
        database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)

if os.environ.get('GAE_ENV'):
    SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
else:
    SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI

SQLALCHEMY_TRACK_MODIFICATIONS = False
