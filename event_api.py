from flask import Blueprint
from data.repositories import eventrepo
from util.api import query_db, format_records

api = Blueprint('event_api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    total_records = query_db(eventrepo.queries['get_all_count'], one=True)[0]
    records = query_db(eventrepo.queries['get_all'])

    return {
        'records': format_records(records), 
        'meta': {
            'total_results': total_records,
        }
    }
