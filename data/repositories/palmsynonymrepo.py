import sqlite3
from data.queries.palmsynonymqueries import queries

# run connect after both synonyms & palms have been written to db
def connect(database_path:str) -> None:
    """Connect palm synonym relationships."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        cur.execute(
            queries['insert'],
        )
        con.commit()

    except sqlite3.Error as error:
        print("Error while connecting palm synonyms in sqlite.", error)
    finally:
        if con:
            con.close()