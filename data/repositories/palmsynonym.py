import sqlite3

queries = {
    "drop": """
DROP TABLE IF EXISTS "PalmSynonym"
    """,
    "create": """
CREATE TABLE IF NOT EXISTS "PalmSynonym" (
    "PalmId" integer NOT NULL,
    "SynonymId" integer NOT NULL,
    FOREIGN KEY (PalmId) REFERENCES "Palm" (Id),
    FOREIGN KEY (SynonymId) REFERENCES "Synonym" (Id)
);
    """
}

# run connect after both synonyms & palms have been written to db
def connect(database_path:str) -> None:
    """Connect palm synonym relationships."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        cur.execute(
            """
INSERT INTO PalmSynonym (PalmId, SynonymId)
SELECT * FROM (
	SELECT 
		S.Id AS SynonymId
		,P.Id AS PalmId
	FROM Synonym AS S
	INNER JOIN Palm AS P ON S.PalmLegacyId = P.LegacyId
)
""",
        )
        con.commit()

    except sqlite3.Error as error:
        print("Error while connecting palm synonyms in sqlite.", error)
    finally:
        if con:
            con.close()