from flask import Blueprint
from util.api import query_db, format_records
from data.queries.datasourcequeries import queries


api = Blueprint('datasource_api', __name__)

@api.route('/', methods=['GET'])
def get_all():
    records = query_db(queries['get_all'])
    total_records = len(records)
    
    return {
        'records': format_records(records), 
        'meta': {
            'total_results': total_records,
        }
    }
