from flask import Blueprint
from data.queries.palmobservationqueries import queries as palmobsqueries
from data.queries.cycadobservationqueries import queries as cycadobsqueries
from util.api import query_db, format_records

api = Blueprint('observation_api', __name__)

@api.route('/palm', methods=['GET'])
def get_all_palm_observations():
    total_records = query_db(palmobsqueries['get_all_count'], one=True)[0]
    records = query_db(palmobsqueries['get_all'])
    return {
        'records': format_records(records),
        'meta': {
            'total_results': total_records,
        }
    }

@api.route('/cycad', methods=['GET'])
def get_all_cycad_observations():
    total_records = query_db(cycadobsqueries['get_all_count'], one=True)[0]
    records = query_db(cycadobsqueries['get_all'])

    return {
        'records': format_records(records),
        'meta': {
            'total_results': total_records,
        }
    }
