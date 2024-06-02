from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.datasource import DataSource, DataSourceSerializer
from data.repositories import datasourcerepo
import json

api = Blueprint('datasource_api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    records = query_db(datasourcerepo.queries['get_all'])
    total_records = len(records)
    
    # convert records to objects so that they can be serialized to json
    objects:list[DataSource] = [datasourcerepo.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=DataSourceSerializer)
    # convert string to json object so it can be returned in the response
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