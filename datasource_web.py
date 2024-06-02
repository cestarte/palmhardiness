from flask import render_template, Blueprint
import requests

web = Blueprint('datasource_web', __name__)

@web.route('/', methods=['GET'])
def index():
    api_response = requests.get('http://127.0.0.1:5000/api/datasource')
    api_json = api_response.json()

    data = {
        'total_results': api_json['meta']['total_results'],
        'results': api_json['records'],
    }
    return render_template('datasource_index.html', data=data)

