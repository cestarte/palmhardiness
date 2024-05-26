from flask import Flask, jsonify, render_template, request, Blueprint, g, current_app, url_for
import requests
from data.models.palm import Palm, PalmSerializer
from data.repositories import palm
import json
import sys

web = Blueprint('web', __name__)

@web.route('/', methods=['GET'])
def index():
    print("palm_web.palm()", file=sys.stderr)
    response = requests.get('http://127.0.0.1:5000/api/palm')
    data = response.json()
    print(response.json(), file=sys.stderr)
    return render_template('palm_index.html', data=data)

