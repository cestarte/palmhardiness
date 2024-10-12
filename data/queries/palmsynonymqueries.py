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
    """,

    "insert": """
    INSERT INTO PalmSynonym (PalmId, SynonymId)
SELECT * FROM (
	SELECT 
		S.Id AS SynonymId
		,P.Id AS PalmId
	FROM Synonym AS S
	INNER JOIN Palm AS P ON S.PalmLegacyId = P.LegacyId
)
    """,
}