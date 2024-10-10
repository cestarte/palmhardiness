from flask import Blueprint, g, current_app, request
import sqlite3
from typing import Optional
from util.api import is_arg_true, format_record, format_records, query_db
from data.repositories import palmquestionrepo as palmquestionrepo
from data.repositories import palmrepo as palmrepo
from data.repositories import palmobservationrepo as palmobservationrepo
import json
import math

api = Blueprint('palm_api', __name__)

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
    total_records = query_db(palmrepo.queries['get_count'], (filter_unobserved, search_term), one=True)[0]
    records = query_db(palmrepo.queries['get_records'], (filter_unobserved, search_term, results_per_page, record_offset))

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

@api.route('/<int:palm_id>', methods=['GET'])
def get_one(palm_id):
    record = query_db(query=palmrepo.queries['get_one'], args=(palm_id,), one=True)
    return format_record(record)

@api.route('/<int:palm_id>/observations', methods=['GET'])
def get_observations(palm_id):
    records = query_db(query=palmobservationrepo.queries['get_all_for_palm'], args=(palm_id,))
    return format_records(records)

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

@api.route('/<int:palm_id>/stat/<stat_name>', methods=['GET'])
def get_stat(palm_id, stat_name):
    record:Optional[sqlite3.row]
    try:
        record = query_db(palmrepo.queries[f'get_stat_{stat_name}'], (palm_id,), one=True)
    except KeyError:
        record = None
    except TypeError:
        record = None

    return format_record(record) if record is not None else json.loads('{"value": null}')
