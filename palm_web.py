from flask import Flask, jsonify, render_template, request, Blueprint, g, current_app, url_for
import requests
import json
import sys
import math
from data.models.palm import Palm, PalmSerializer
from data.repositories import palm
import palm_api

web = Blueprint('web', __name__)

@web.route('/', methods=['GET'])
def index():
    page = request.args.get('page',1, type=int)
    results_per_page = request.args.get('results_per_page', 50, type=int)

    #request_url = url_for(palm_api.get_all, offset=page*results_per_page, num_results=results_per_page)
    #response = requests.get(request_url)
    
    api_response = requests.get('http://127.0.0.1:5000/api/palm', params={'offset': page*results_per_page, 'num_results': results_per_page})
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
        'results': api_json['records']
    }
    return render_template('palm_index.html', data=data)

