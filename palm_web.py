from flask import Flask, jsonify, render_template, request, Blueprint, g, current_app, url_for
import requests
import json
import sys
import math
from data.models.palm import Palm, PalmSerializer
from data.repositories import palm
import palm_api as papi

web = Blueprint('web', __name__)

@web.route('/', methods=['GET'])
def index():
    page = request.args.get('page',1, type=int)
    results_per_page = request.args.get('results_per_page', 25, type=int)
    search_term = request.args.get('search', None, type=str)

    #api_response = requests.get(url_for('papi.palm'), params={'offset': page*results_per_page, 'num_results': results_per_page, 'search': search_term})
    api_response = requests.get('http://127.0.0.1:5000/api/palm', params={'offset': page*results_per_page, 'num_results': results_per_page, 'search': search_term})
    api_json = api_response.json()

    total_pages = math.ceil(api_json['meta']['total_results'] / results_per_page)

    next_page_url = None
    if page+1 <= total_pages:
        next_page_url = url_for('web.index', page=page+1, results_per_page=results_per_page)
    previous_page_url = None
    if page-1 > 0:
        previous_page_url = url_for('web.index', page=page-1, results_per_page=results_per_page)


    data = {
        'page': page,
        'results_per_page': results_per_page,
        'results_on_this_page': len(api_json['records']),
        'total_results': api_json['meta']['total_results'],
        'total_pages': total_pages,
        'next_page_url': next_page_url,
        'previous_page_url': previous_page_url,
        'results': api_json['records'],
        'search': search_term,
    }
    return render_template('palm_index.html', data=data)

