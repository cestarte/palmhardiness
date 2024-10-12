from flask import Blueprint
from data.repositories import palmobservationrepo
from data.repositories import cycadobservationrepo
from util.api import query_db

api = Blueprint('observation_api', __name__)

@api.route('/palm', methods=['GET'])
def get_all_palm_observations():
    total_records = query_db(palmobservationrepo.queries['get_all_count'], one=True)[0]
    records = query_db(palmobservationrepo.queries['get_all'])

    return {
        'records': [dict(r) for r in records],
        'meta': {
            'total_results': total_records,
        }
    }

@api.route('/cycad', methods=['GET'])
def get_all_cycad_observations():
    total_records = query_db(cycadobservationrepo.queries['get_all_count'], one=True)[0]
    records = query_db(cycadobservationrepo.queries['get_all'])

    return {
        'records': [dict(r) for r in records],
        'meta': {
            'total_results': total_records,
        }
    }
