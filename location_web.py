from flask import render_template, Blueprint

web = Blueprint('location_web', __name__)

@web.route('/', methods=['GET'])
def index():
    return render_template('location_index.html')
