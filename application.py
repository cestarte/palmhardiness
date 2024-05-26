from http import HTTPStatus
from flask import Flask, request, jsonify, make_response, render_template, g
import sqlite3
from werkzeug.exceptions import HTTPException
import json
from exceptions import InvalidApiUsage
import palm_api

app = Flask(__name__)
app.config['Database'] = './palmhardiness.db'

#app.register_blueprint(event, __name__)
app.register_blueprint(palm_api.api , url_prefix='/api/palm')
#app.register_blueprint(create, __name__)
#app.register_blueprint(zone, __name__)


# https://flask.palletsprojects.com/en/3.0.x/errorhandling/#error-logging-tools
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle non-HTTP errors."""
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    g.e = e
    # now handling non-HTTP exceptions only
    return render_template("500_generic.html"), 500

# https://flask.palletsprojects.com/en/3.0.x/errorhandling/#error-logging-tools
@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })

    if request.path.startswith('/api/'):
        response.content_type = "application/json"
        return response
    else:
        return render_template("error", response)



@app.route('/api/everything/<int:page_num>', methods=['GET'])
def everything(page_num):
    #page_num = request.arg.get('page_num', 0)
    if not page_num:
        raise InvalidApiUsage("No page number provided!")
    cur = get_db().cursor()
    cur.execute("""
SELECT * FROM (
	SELECT 
		O.ROWID AS [Row Id]
		,O.LowTemp
	    ,P.Genus
	    ,P.Species
	    ,P.Variety
	    ,Z.Name AS [USDA Zone]
	    ,D.Text AS [Result]
	    ,O.City
	    ,O.Country
	    ,O.State
	    ,E.Name AS [Event Name]
	    ,E.Description AS [Event Desc]
	FROM PalmObservation AS O
	INNER JOIN Palm AS P ON O.PalmId = P.Id
	LEFT JOIN [Zone] AS Z ON P.ZoneId = Z.Id
	LEFT JOIN Damage AS D ON O.DamageId = D.Id
	LEFT JOIN [Event] AS E ON O.EventId = E.Id
	ORDER BY LowTemp ASC, Genus ASC, Species ASC, 
	    Variety ASC, [Event Name] ASC
) WHERE [Row Id] IN (
	SELECT ROWID 
    FROM PalmObservation          
	LEFT JOIN Palm AS P ON O.PalmId = P.Id
    ORDER BY LowTemp ASC, Genus ASC, Species ASC,   
	    Variety ASC, [Event Name] ASC  
            LIMIT 20 OFFSET ?
)
    """, (page_num))
    rows = cur.fetchall()
    return rows, 200
    #return jsonify({'page_num': page_num})


@app.route('/')
def index():
    cur = get_db().cursor()
    cur.execute("""
SELECT 
	O.LowTemp
	,P.Genus
	,P.Species
	,P.Variety
	,Z.Name AS [USDA Zone]
	,D.Text AS [Result]
	,O.City
	,O.Country
	,O.State
	,E.Name AS [Event Name]
	,E.Description AS [Event Desc]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  LEFT JOIN [Zone] AS Z ON P.ZoneId = Z.Id
  LEFT JOIN Damage AS D ON O.DamageId = D.Id
  LEFT JOIN [Event] AS E ON O.EventId = E.Id
ORDER BY LowTemp ASC, Genus ASC, Species ASC, 
  Variety ASC, [Event Name] ASC
""")
    rows = cur.fetchall()
    return render_template('everything.html', rows=rows)


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


DATABASE = './palmhardiness.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
