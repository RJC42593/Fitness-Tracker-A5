import atexit

from flask import current_app
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def init_database(app):
    uri = app.config['MONGODB_URI']

    if not uri:
        app.extensions['mongo'] = None
        return

    try:
        client = MongoClient(
            uri,
            connect=False,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
    except (PyMongoError, ValueError):
        raise RuntimeError(
            'Invalid MongoDB connection settings. Check your local .env file.'
        ) from None

    app.extensions['mongo'] = client
    atexit.register(client.close)


def get_database():
    client = current_app.extensions['mongo']

    if client is None:
        raise RuntimeError('Set MONGODB_URI in your local .env file first.')

    return client.get_database(current_app.config['MONGODB_DB'])
