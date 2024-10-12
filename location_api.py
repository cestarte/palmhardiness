from flask import Blueprint, request
from data.repositories import locationrepo as locationrepo
import json
import math
from util.api import query_db, format_record, format_records

api = Blueprint('location_api', __name__)

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
    if search_term is not None and len(search_term) < 3:
        search_term = None

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    total_records = query_db(locationrepo.queries['get_count'], (search_term,), one=True)[0]
    records = query_db(locationrepo.queries['get_records'], (search_term, results_per_page, record_offset))

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

@api.route('/<int:location_id>', methods=['GET'])
def get_one(location_id):
    record = query_db(query=locationrepo.queries['get_one'], args=(location_id,), one=True)
    if record is not None:
        return format_record(record)
    return json.dumps(None)

@api.route('/<int:location_id>/stat/<stat_name>', methods=['GET'])
def get_stat(location_id, stat_name):
    record = query_db(locationrepo.queries[f'get_stat_{stat_name}'], (location_id,), one=True)
    if record is not None and record['value'] is not None:
        return json.loads(f'{{"value": "{str(record["value"])}"}}')
    return json.loads(None)
