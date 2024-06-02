from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.palm import Palm, PalmSerializer
from data.repositories import palmrepo as palm
import json
import sys
import math

api = Blueprint('palm_api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    page = request.args.get('page', 1, type=int)
    results_per_page = request.args.get('results_per_page', 15, type=int)
    search_term = request.args.get('search', None, type=str)

    # sanity check the inputs
    if page < 1:
        page = 1
    if results_per_page < 1:
        results_per_page = 15
    if results_per_page > 100:
        results_per_page = 100

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    if search_term is None or search_term == '':
        # no term provided, get all records
        total_records = query_db(palm.queries['get_count'], one=True)[0]
        records = query_db(palm.queries['get_all'], (results_per_page, record_offset))
    else:
        total_records = query_db(palm.queries['search_count'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',), one=True)[0]
        records = query_db(palm.queries['search_all'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%', results_per_page, record_offset))

    total_pages = math.ceil(total_records / results_per_page)
    has_previous_page = False
    has_next_page = False
    if total_pages == 0:
        page = 0
    if page > 1:
        has_previous_page = True
    if total_pages > page:
        has_next_page = True
    
    # convert records to objects so that they can be serialized to json
    objects:list[Palm] = [palm.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=PalmSerializer)
    # convert string to json object so it can be returned in the response
    objects_json = json.loads(objects_json_string)

    return {
        'records': objects_json, 
        'meta': {
            'offset': record_offset, 
            'results_on_this_page': len(objects), 
            'total_results': total_records,
            'total_pages': total_pages,
            'has_previous_page': has_previous_page,
            'has_next_page': has_next_page,
            'page': page,
            'results_per_page': results_per_page,
            'search': search_term,
        }
    }

@api.route('/old', methods=['GET'])
def get_all_old():
    offset = request.args.get('offset', 0, type=int)
    num_results = request.args.get('num_results', 25, type=int)
    search_term = request.args.get('search', None, type=str)
    total_records = 0
    records = 0

    if search_term is None or search_term == '':
        # no term provided, get all records
        total_records = query_db(palm.queries['get_count'], one=True)[0]
        records = query_db(palm.queries['get_all'], (num_results, offset))
    else:
        total_records = query_db(palm.queries['search_count'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',), one=True)[0]
        records = query_db(palm.queries['search_all'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%', num_results, offset))

    
    # convert records to objects so that they can be serialized to json
    objects:list[Palm] = [palm.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=PalmSerializer)
    # convert string to json object so it can be returned in the response
    objects_json = json.loads(objects_json_string)

    return {
        'records': objects_json, 
        'meta': {'offset': offset, 'num_results': len(objects), 'total_results': total_records}
    }

@api.route('/<int:palm_id>', methods=['GET'])
def get_one(palm_id):
    record = query_db(query=palm.queries['get_one'], args=(palm_id,), one=True)
    if record is not None:
        obj = palm.read_from_row(record)
        return json.dumps(obj, cls=PalmSerializer)
    return json.dumps(None)
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