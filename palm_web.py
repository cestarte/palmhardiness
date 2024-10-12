from flask import render_template, Blueprint 
import data.repositories.palmrepo as palmrepo
from util.api import query_db, format_record

web = Blueprint('palm_web', __name__)

@web.route('/', methods=['GET'])
def index():
    return render_template('palm_index.html')

@web.route('/<int:palm_id>', methods=['GET'])
def detail(palm_id):
    palm = query_db(palmrepo.queries['get_one'], (palm_id,), one=True)

    if palm is not None:
            return render_template('palm_detail.html', data=format_record(palm))
    else:
         return render_template('404_generic.html'), 404

@web.route('/questions', methods=['GET'])
def questions():
     return render_template('palm_questions.html')