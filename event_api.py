from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.event import Event, EventSerializer
from data.repositories import eventrepo
import json
import math

api = Blueprint('event_api', __name__)

def is_arg_true(value:str) -> bool:
    return value.lower() in ['true', 'yes', '1']

@api.route('/', methods=['GET'])
def get_all():
    total_records = query_db(eventrepo.queries['get_all_count'], one=True)[0]
    records = query_db(eventrepo.queries['get_all'])

    # convert records to objects so that they can be serialized to json
    objects:list[Event] = [eventrepo.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=EventSerializer)
    objects_json = json.loads(objects_json_string)

    return {
        'records': objects_json, 
        'meta': {
            'total_results': total_records,
        }
    }

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