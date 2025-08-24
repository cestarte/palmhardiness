from flask import Blueprint, request
import sqlite3
from typing import Optional
from util.api import is_arg_true, format_record, format_records, query_db
from data.queries.palmqueries import queries as palmqueries
from data.queries.palmobservationqueries import queries as palmobsqueries
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
    if search_term is not None and len(search_term) < 2:
        search_term = None

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    total_records = query_db(palmqueries['get_count'], (filter_unobserved, search_term), one=True)[0]
    records = query_db(palmqueries['get_records'], (filter_unobserved, search_term, results_per_page, record_offset))

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
    record = query_db(palmqueries['get_one'], args=(palm_id,), one=True)
    return format_record(record)

@api.route('/<int:palm_id>/observations', methods=['GET'])
def get_observations(palm_id):
    records = query_db(palmobsqueries['get_all_for_palm'], args=(palm_id,))
    return format_records(records)

@api.route('/lowestsurvived', methods=['GET'])
def get_lowest_survived():
    page = request.args.get('page', 1, type=int)
    results_per_page = request.args.get('results_per_page', 15, type=int)
    search_term = request.args.get('search', None, type=str)
    sort_by_ui = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    # sanity check the inputs
    if page < 1:
        page = 1
    if results_per_page < 1:
        results_per_page = 15
    if results_per_page > 100:
        results_per_page = 100
    if search_term is not None and len(search_term) < 2:
        search_term = None

    # translate the UI sort_by column to the actual SQL column name
    sort_by = sort_by_ui.upper()
    if sort_by == 'NAME':
        sort_by = '[Name]'
    elif sort_by == 'MIN':
        sort_by = '[Min]'
    elif sort_by == 'MAX':
        sort_by = '[Max]'
    elif sort_by == 'AVERAGE':
        sort_by = '[Average]'
    elif sort_by == 'RECORDS':
        sort_by = '[Records]'
    else:
        sort_by = '[Name]'

    # translate the UI sort_order to the actual SQL sort order
    if not sort_order or sort_order.upper() == 'DESC':
        sort_order = 'DESC'
    else:
        sort_order = 'ASC'

    total_pages = 0
    total_records = 0
    records = 0
    record_offset = (page-1) * results_per_page
    total_records = query_db(palmqueries['get_count_lowest_survived_for_all_palms'], args=(search_term,), one=True)[0]
    adjusted_query = palmqueries['get_lowest_survived_for_all_palms'] + f' ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?'
    #print("ADJUSTED QUERY: ", adjusted_query)
    records = query_db(adjusted_query, (search_term, results_per_page, record_offset))

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
            'sort_by': sort_by_ui,
            'sort_order': sort_order,
        }
    }

@api.route('/<int:palm_id>/stat/<stat_name>', methods=['GET'])
def get_stat(palm_id, stat_name):
    record:Optional[sqlite3.row]
    stat_name = stat_name.upper()
    query_name = ''
    print("STAT NAME:", stat_name)
    try:
        if stat_name == 'NUMEVENTS':
            query_name = 'get_stat_num_events'
        elif stat_name == 'LOWESTSURVIVED':
            query_name = 'get_stat_lowest_survived'
        elif stat_name == 'NUMOBSERVATIONS':
            query_name = 'get_stat_num_observations'
        else:
            raise KeyError(f'Unknown stat name: {stat_name}')
        

        record = query_db(palmqueries[f'{query_name}'], (palm_id,), one=True)
    except KeyError:
        record = None
    except TypeError:
        record = None

    return format_record(record) if record is not None else json.loads('{"value": null}')

@api.route('/temps', methods=['GET'])
def get_temps():
    page = request.args.get('page', 1, type=int)
    results_per_page = request.args.get('results_per_page', 15, type=int)
    search_term = request.args.get('search', None, type=str)
    sort_by_ui = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    # sanity check the inputs
    if page < 1:
        page = 1
    if results_per_page < 1:
        results_per_page = 15
    if results_per_page > 100:
        results_per_page = 100
    if search_term is not None and len(search_term) < 2:
        search_term = None

    # translate the UI sort_by column to the actual SQL column name
    sort_by = sort_by_ui.upper()
    print('SORT BY:', sort_by)

    if sort_by == 'LONGNAME':
        sort_by = '[LongName]'
    elif sort_by == 'COMMONNAME':
        sort_by = '[CommonName]'
    elif sort_by == 'LOWESTSURVIVEDTEMP':
        sort_by = '[LowestSurvivedTemp]'
    elif sort_by == 'LOWESTDAMAGINGTEMP':
        sort_by = '[LowestDamagingTemp]'
    elif sort_by == 'LOWESTUNDAMAGEDTEMP':
        sort_by = '[LowestUndamagedTemp]'
    elif sort_by == 'HIGHESTDAMAGINGTEMP':
        sort_by = '[HighestDamagingTemp]'
    elif sort_by == 'HIGHESTKILLINGTEMP':
        sort_by = '[HighestKillingTemp]'
    elif sort_by == 'TOTALOBSERVATIONS':
        sort_by = '[TotalObservations]'
    elif sort_by == 'SURVIVED30COUNT':
        sort_by = '[Survived30Count]'
    elif sort_by == 'SURVIVED25COUNT':
        sort_by = '[Survived25Count]'
    elif sort_by == 'SURVIVED20COUNT':
        sort_by = '[Survived20Count]'
    elif sort_by == 'SURVIVED15COUNT':
        sort_by = '[Survived15Count]'
    elif sort_by == 'SURVIVED10COUNT':
        sort_by = '[Survived10Count]'
    elif sort_by == 'SURVIVED5COUNT':
        sort_by = '[Survived5Count]'
    else:
        sort_by = '[LongName]'

    # translate the UI sort_order to the actual SQL sort order
    if not sort_order or sort_order.upper() == 'DESC':
        sort_order = 'DESC'
    else:
        sort_order = 'ASC'

    total_pages = 0
    total_records = query_db(palmqueries['get_count_temps'], args=(search_term,), one=True)[0]
    records = 0
    record_offset = (page-1) * results_per_page
    adjusted_query = palmqueries['get_temps'] + f' ORDER BY {sort_by} {sort_order} NULLS LAST LIMIT ? OFFSET ?'
    #print("ADJUSTED QUERY: ", adjusted_query)
    records = query_db(adjusted_query, (search_term, results_per_page, record_offset))

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
            'sort_by': sort_by_ui,
            'sort_order': sort_order,
        }
    }