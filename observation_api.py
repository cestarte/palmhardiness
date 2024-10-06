from flask import Blueprint, g, current_app, request
import sqlite3
from data.models.palmobservation import PalmObservation, PalmObservationSerializer
from data.repositories import palmobservationrepo
from data.repositories import cycadobservationrepo
import json

api = Blueprint('observation_api', __name__)

def is_arg_true(value:str) -> bool:
    return value.lower() in ['true', 'yes', '1']

@api.route('/palm', methods=['GET'])
def get_all_palm_observations():
    total_records = query_db(palmobservationrepo.queries['get_all_count'], one=True)[0]
    records = query_db(palmobservationrepo.queries['get_all'])

    return {
        #'records': objects_json, 
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
        #'records': objects_json, 
        'records': [dict(r) for r in records],
        'meta': {
            'total_results': total_records,
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