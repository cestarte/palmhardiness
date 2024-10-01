from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.palm import Palm, PalmSerializer
from data.models.palmobservation import PalmObservation, PalmObservationSerializer
from data.models.lowestsurviving import LowestSurviving, LowestSurvivingSerializer
from data.repositories import palmquestionrepo as palmquestionrepo
from data.repositories import palmrepo as palm
from data.repositories import palmobservationrepo as palmobservation
import json
import math

api = Blueprint('palm_api', __name__)

def is_arg_true(value:str) -> bool:
    return value.lower() in ['true', 'yes', '1']


@api.route('/', methods=['GET'])
def get_all():
    page = request.args.get('page', 1, type=int)
    results_per_page = request.args.get('results_per_page', 15, type=int)
    search_term = request.args.get('search', None, type=str)
    filter_unobserved = request.args.get('filter_unobserved', True, type=is_arg_true)

    # sanity check the inputs
    if page < 1:
        page = 1
    if results_per_page < 1:
        results_per_page = 15
    if results_per_page > 100:
        results_per_page = 100
    if search_term is not None and len(search_term) < 3:
        search_term = None

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    total_records = query_db(palm.queries['get_count'], (filter_unobserved, search_term), one=True)[0]
    records = query_db(palm.queries['get_records'], (filter_unobserved, search_term, results_per_page, record_offset))

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

@api.route('/<int:palm_id>', methods=['GET'])
def get_one(palm_id):
    record = query_db(query=palm.queries['get_one'], args=(palm_id,), one=True)
    if record is not None:
        obj = palm.read_from_row(record)
        return json.dumps(obj, cls=PalmSerializer)
    return json.dumps(None)

@api.route('/<int:palm_id>/observations', methods=['GET'])
def get_observations(palm_id):
    records = query_db(query=palmobservation.queries['get_all_for_palm'], args=(palm_id,))
    objects:list[PalmObservation] = [palmobservation.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=PalmObservationSerializer)
    objects_json = json.loads(objects_json_string)
    return objects_json

@api.route('/lowestsurviving', methods=['GET'])
def get_lowest_surviving():
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
    if search_term is not None and len(search_term) < 3:
        search_term = None

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    total_records = query_db(palmquestionrepo.queries['get_count_lowest_surviving_for_all_palms'], args=(search_term,), one=True)[0]
    records = query_db(palmquestionrepo.queries['get_lowest_surviving_for_all_palms'], (search_term, results_per_page, record_offset))

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
    objects:list[LowestSurviving] = [palmquestionrepo.read_lowest_surviving_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=LowestSurvivingSerializer)
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