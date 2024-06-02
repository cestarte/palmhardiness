from http import HTTPStatus
from flask import Flask, redirect, jsonify, make_response, render_template, g, url_for
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from exceptions import InvalidApiUsage
from palm_api import api as palm_api
import palm_web
from datasource_api import api as datasource_api
from datasource_web import web as datasource_web
import requests
import sqlite3

app = Flask(__name__)
CORS(app)
app.config['Database'] = './palmhardiness.db'

app.register_blueprint(palm_web.web, url_prefix='/palm')
app.register_blueprint(datasource_web, url_prefix='/datasource')

app.register_blueprint(palm_api , url_prefix='/api/palm')
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

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('web.index'))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)
