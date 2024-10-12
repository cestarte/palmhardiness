from flask import render_template, Blueprint
import data.repositories.cycadrepo as cycadrepo
from util.api import query_db, format_record

web = Blueprint('cycad_web', __name__)

@web.route('/', methods=['GET'])
def index():
    return render_template('cycad_index.html')

@web.route('/<int:cycad_id>', methods=['GET'])
def detail(cycad_id):
    cycad = query_db(cycadrepo.queries['get_one'], (cycad_id,), one=True)

    if cycad is not None:
        return render_template('cycad_detail.html', data=format_record(cycad))
    else:
         return render_template('404_generic.html'), 404
