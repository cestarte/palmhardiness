from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.palm import Palm, PalmSerializer
from data.repositories import palm
import json
import sys

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    offset = request.args.get('offset', 0, type=int)
    num_results = request.args.get('num_results', 25, type=int)
    total_records = query_db(palm.queries['get_count'], one=True)[0]
    records = query_db(palm.queries['get_all'], (num_results, offset))
    
    # convert records to objects so that they can be serialized to json
    objects:list[Palm] = [palm.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=PalmSerializer)
    # convert string to json object so it can be returned in the response
    objects_json = json.loads(objects_json_string)

    return {
        'records': objects_json, 
        'meta': {'offset': offset, 'num_results': len(objects), 'total_results': total_records}
    }
    #return json.dumps(objs, cls=PalmSerializer)

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