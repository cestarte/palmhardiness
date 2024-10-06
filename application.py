from http import HTTPStatus
from flask import Flask, redirect, jsonify, make_response, render_template, g, url_for
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from exceptions import InvalidApiUsage
from palm_api import api as palm_api
from cycad_api import api as cycad_api
from location_api import api as location_api
from event_api import api as event_api
import palm_web
import cycad_web
import location_web
from datasource_api import api as datasource_api
from datasource_web import web as datasource_web
import requests
import sqlite3
# origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
app = Flask(__name__)
CORS(app, 
    send_wildcard=True,
    vary_header=True,
    resources= {
        r"/api/*": {"origins": "*"},
        r"/*": {"origins": "*"}
    })

#put this snippet ahead of all your bluprints
@app.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

app.config['Database'] = './palmhardiness.db'

app.register_blueprint(palm_web.web, url_prefix='/palm', name='palm_web')
app.register_blueprint(cycad_web.web, url_prefix='/cycad', name='cycad_web')
app.register_blueprint(location_web.web, url_prefix='/location', name='location_web')
app.register_blueprint(datasource_web, url_prefix='/datasource')

app.register_blueprint(palm_api , url_prefix='/api/palm', name='palm_api')
app.register_blueprint(cycad_api , url_prefix='/api/cycad', name='cycad_api')
app.register_blueprint(location_api , url_prefix='/api/location', name='location_api')
app.register_blueprint(event_api , url_prefix='/api/event', name='event_api')
app.register_blueprint(datasource_api , url_prefix='/api/datasource')

@app.route('/about', methods=['GET'])
def about():
    api_response = requests.get('http://127.0.0.1:5000/api/datasource')
    api_json = api_response.json()

    data = {
        'total_results': api_json['meta']['total_results'],
        'results': api_json['records'],
    }
    return render_template('about.html', data=data)

@app.route('/map', methods=['GET'])
def map():
    return render_template('map.html')

@app.route('/location', methods=['GET'])
def location():
    return redirect(url_for('location_web.index'))

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('palm_web.index'))



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)
