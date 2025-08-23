queries = {
    "drop": "DROP TABLE IF EXISTS cycad",
    
    "create": """
CREATE TABLE IF NOT EXISTS "Cycad" (
"Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
"LegacyId" integer,
"Genus" varchar(512) NOT NULL,
"Species" varchar(256),
"Variety" varchar(256),
"CommonName" varchar(256),
"ZoneId" integer NOT NULL,
"LastModified" timestamp NOT NULL,
"WhoModified" varchar(128) NOT NULL,
FOREIGN KEY (ZoneId) REFERENCES "Zone" (Id)
);
    """,

    "insert": """
INSERT INTO Cycad (Id, LegacyId, Genus, Species, Variety, CommonName, ZoneId, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    "select_by_legacy_id": """
SELECT Id
FROM Cycad
WHERE LegacyId = ?
LIMIT 1
    """,

# Query takes 3 parameters: genus, species, variety
  "select_by_genus_species_variety": """
SELECT Id
FROM Cycad
WHERE Genus = ?1 
  AND (CASE WHEN ?2 = 'None' THEN Species IS NULL ELSE Species IS ?2 END)
  AND (CASE WHEN ?3 = 'None' THEN Variety IS NULL ELSE Variety IS ?3 END)
    """,

    "get_count": """
SELECT COUNT(*) as count
FROM (
        WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
        SELECT COUNT(*) as ObservationCount
        FROM Cycad, vars
        LEFT JOIN Zone ON Cycad.ZoneId = Zone.Id
        LEFT JOIN CycadObservation ON Cycad.Id = CycadObservation.CycadId
        -- Allow unobserved unless we are filtering them out
        WHERE (CycadObservation.Id IS NOT NULL OR filterObserved = 0)
        -- If there is a search term, then filter on it
            AND (term is NULL 
                OR INSTR(UPPER(Genus), term) > 0 
                OR INSTR(UPPER(Species), term) > 0 
                OR INSTR(UPPER(Variety), term) > 0 
                OR INSTR(UPPER(CommonName), term) > 0
                OR INSTR(UPPER(Zone.Name), term) > 0
    )
    GROUP BY Cycad.Id
)
    """,

    "get_records": """
WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
SELECT Cycad.*
    ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, ''))  AS CycadName
    ,Zone.Name as ZoneName
    ,COUNT(CycadObservation.Id) as ObservationCount
FROM Cycad, vars
LEFT JOIN Zone ON Cycad.ZoneId = Zone.Id
LEFT JOIN CycadObservation ON Cycad.Id = CycadObservation.CycadId
-- Allow unobserved unless we are filtering them out
WHERE (CycadObservation.Id IS NOT NULL OR filterObserved = 0)
-- If there is a search term, then filter on it
    AND (term is NULL 
        OR INSTR(UPPER(Genus), term) > 0 
        OR INSTR(UPPER(Species), term) > 0 
        OR INSTR(UPPER(Variety), term) > 0 
        OR INSTR(UPPER(CommonName), term) > 0
        OR INSTR(UPPER(Zone.Name), term) > 0
    )
GROUP BY Cycad.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,


    "get_one": """
SELECT Cycad.*
    ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, ''))  AS CycadName
    ,Zone.Name as ZoneName
	,(SELECT COUNT(*) 
		FROM CycadObservation
	WHERE CycadId = Cycad.Id) AS [ObservationCount]
FROM Cycad
LEFT JOIN Zone ON Cycad.ZoneId = Zone.Id
WHERE Cycad.Id = ?
    """,
}