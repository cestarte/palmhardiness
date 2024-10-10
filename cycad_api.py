import sqlite3
import json
import math
from flask import Blueprint, g, current_app, request
from util.api import is_arg_true, query_db, format_record, format_records
from data.models.cycad import Cycad
from data.repositories import cycadrepo
from data.repositories import cycadobservationrepo

api = Blueprint('cycad_api', __name__)

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
    total_records = query_db(cycadrepo.queries['get_count'], (filter_unobserved, search_term), one=True)[0]
    records = query_db(cycadrepo.queries['get_records'], (filter_unobserved, search_term, results_per_page, record_offset))

    total_pages = math.ceil(total_records / results_per_page)
    has_previous_page = False
    has_next_page = False
    if total_pages == 0:
        page = 0
    if page > 1:
        has_previous_page = True
    if total_pages > page:
        has_next_page = True
    
    return {
        'records': format_records(records), 
        'meta': {
            'offset': record_offset, 
            'results_on_this_page': len(records), 
            'total_results': total_records,
            'total_pages': total_pages,
            'has_previous_page': has_previous_page,
            'has_next_page': has_next_page,
            'page': page,
            'results_per_page': results_per_page,
            'search': search_term,
        }
    }


    offset = request.args.get('offset', 0, type=int)
    num_results = request.args.get('num_results', 25, type=int)
    search_term = request.args.get('search', None, type=str)
    total_records = 0
    records = 0

    if search_term is None or search_term == '':
        # no term provided, get all records
        total_records = query_db(cycad.queries['get_count'], one=True)[0]
        records = query_db(cycad.queries['get_all'], (num_results, offset))
    else:
        total_records = query_db(cycad.queries['search_count'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',), one=True)[0]
        records = query_db(cycad.queries['search_all'], (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%', num_results, offset))

    
    # convert records to objects so that they can be serialized to json
    objects:list[Cycad] = [cycad.read_from_row(row) for row in records]
    objects_json_string = json.dumps(objects, cls=CycadSerializer)
    # convert string to json object so it can be returned in the response
    objects_json = json.loads(objects_json_string)

    return {
        'records': objects_json, 
        'meta': {'offset': offset, 'num_results': len(objects), 'total_results': total_records}
    }

@api.route('/<int:cycad_id>', methods=['GET'])
def get_one(cycad_id):
    record = query_db(query=cycadrepo.queries['get_one'], args=(cycad_id,), one=True)
    return format_record(record)

@api.route('/<int:cycad_id>/observations', methods=['GET'])
def get_observations(cycad_id):
    records = query_db(query=cycadobservationrepo.queries['get_all_for_cycad'], args=(cycad_id,))
    return format_records(records)

