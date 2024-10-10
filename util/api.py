from typing import Optional
from flask import g, current_app
import sqlite3

def is_arg_true(value:str) -> bool:
    """ Returns True if the value is 'true', 'yes', or '1'. For flask query params """
    return value.lower() in ['true', 'yes', '1']

def format_record(record:Optional[sqlite3.Row]) -> Optional[dict]:
    """ Converts a sqlite3.Row object to a dictionary """
    if record is None:
        return None

    converted_record = dict(record)
    # now make the keys lowercase
    formatted_record = {}
    for k, v in converted_record.items():
        formatted_record[k.lower()] = v

    return formatted_record

def format_records(records:list[sqlite3.Row]) -> list[dict]:
    """ Converts a list of sqlite3.Row objects to a list of dictionaries """
    new_records:list[dict] = []
    for r in records:
        new_records.append(format_record(r))
    return new_records

def get_db():
    """ Returns a connection to the database """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['Database'])
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    """ Executes a query on the database. Use one=True to return a single record """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

