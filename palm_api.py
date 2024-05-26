from flask import Blueprint, g, current_app
import sqlite3
from data.models.palm import Palm, PalmSerializer
from data.repositories import palm
import json

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    records = query_db(palm.queries['get_all'])
    objs:list[Palm] = [palm.read_from_row(row) for row in records]
    return json.dumps(objs, cls=PalmSerializer)
    #return [json.dumps(o, cls=PalmSerializer) for o in objs]

@api.route('/<int:palm_id>', methods=['GET'])
def palm_by_id(palm_id):
    record = query_db(query=palm.queries['get_one'], args=(palm_id,), one=True)
    obj = palm.read_from_row(record)
    return json.dumps(obj, cls=PalmSerializer)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['Database'])
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv