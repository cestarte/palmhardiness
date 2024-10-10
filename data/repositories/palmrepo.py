import openpyxl
import sqlite3
from util.string import clean
from data.models.palm import Palm

queries = {
    "get_count": """
SELECT COUNT(*) as count
FROM (
        WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
        SELECT COUNT(*) as ObservationCount
        FROM Palm, vars
        LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
        LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
        -- Allow unobserved unless we are filtering them out
        WHERE (PalmObservation.Id IS NOT NULL OR filterObserved = 0)
        -- If there is a search term, then filter on it
            AND (term is NULL 
                OR INSTR(UPPER(Genus), term) > 0 
                OR INSTR(UPPER(Species), term) > 0 
                OR INSTR(UPPER(Variety), term) > 0 
                OR INSTR(UPPER(CommonName), term) > 0
                OR INSTR(UPPER(Zone.Name), term) > 0
    )
    GROUP BY Palm.Id
)
    """,

    "get_records": """
WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
SELECT Palm.*
    ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, ''))  AS LongName
    ,Zone.Name as ZoneName
    ,COUNT(PalmObservation.Id) as ObservationCount
FROM Palm, vars
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
-- Allow unobserved unless we are filtering them out
WHERE (PalmObservation.Id IS NOT NULL OR filterObserved = 0)
-- If there is a search term, then filter on it
    AND (term is NULL 
        OR INSTR(UPPER(Genus), term) > 0 
        OR INSTR(UPPER(Species), term) > 0 
        OR INSTR(UPPER(Variety), term) > 0 
        OR INSTR(UPPER(CommonName), term) > 0
        OR INSTR(UPPER(Zone.Name), term) > 0
    )
GROUP BY Palm.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,


    "get_one": """
SELECT Palm.*
    ,TRIM(COALESCE(Palm.Genus, '') || ' ' || COALESCE(Palm.Species, '') || ' ' || COALESCE(Palm.Variety, '')) AS PalmName
    ,Zone.Name as ZoneName
	,(SELECT COUNT(*) 
		FROM PalmObservation
	WHERE PalmId = Palm.Id) AS [ObservationCount]
FROM Palm
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
WHERE Palm.Id = ?
    """,


    "drop": """
DROP TABLE IF EXISTS "Palm"
    """,


    "create": """
CREATE TABLE IF NOT EXISTS "Palm" (
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


    "get_all_with_palmobservation_count": """
SELECT Palm.*
    ,Zone.Name as ZoneName
    ,COUNT(PalmObservation.Id) as ObservationCount
FROM Palm
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
GROUP BY Palm.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,

    "get_observations_for_palm": """
SELECT PalmObservation.LegacyId
	,PalmObservation.LastModified
	,PalmObservation.WhoModified
	,PalmObservation.WhoReported
	,PalmObservation.LowTemp
    ,TRIM(COALESCE(Palm.Genus, '') || ' ' || COALESCE(Palm.Species, '') || ' ' || COALESCE(Palm.Variety, '')) AS PalmName
    ,Palm.LegacyId as PalmLegacyId
    ,Palm.Genus as PalmGenus
    ,Palm.Species as PalmSpecies
    ,Palm.Variety as PalmVariety
    ,Palm.CommonName as PalmCommonName
    ,Palm.ZoneId as PalmZoneId
    ,Zone.Name as ZoneName
    ,Location.City as LocationCity
    ,Location.State as LocationState
    ,Location.Country as LocationCountry
    ,Location.Latitude AS LocationLatitude
    ,Location.Longitude AS LocationLongitude
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
FROM PalmObservation
LEFT JOIN Palm ON PalmObservation.PalmId = Palm.Id
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN Location ON PalmObservation.LocationId = Location.Id
WHERE PalmObservation.PalmId = ?
ORDER BY PalmObservation.LowTemp DESC
    """,

    "get_stat_LOWESTSURVIVED": """
SELECT MIN(o.LowTemp) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
WHERE p.Id = ?
    """,

    "get_stat_NUMOBSERVATIONS": """
SELECT COUNT(*) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
WHERE p.Id = ?
    """,

    "get_stat_NUMEVENTS": """
SELECT COUNT(event) AS [value]
FROM (
    SELECT DISTINCT(e.Id) AS [event]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
    GROUP BY e.Id
)
    """,

    "get_stat_MOSTREPORTEDBY": """
SELECT [who] AS [value]
FROM (
    SELECT 
		e.WhoReported AS [who]
		,COUNT(e.WhoReported) AS [count]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
    GROUP BY e.WhoReported
)
ORDER BY [count] DESC
LIMIT 1
    """,

    "get_stat_MOSTCOMMONLOCATION": """
SELECT [location] AS [value]
	,COUNT(*) AS [count]
FROM (
    SELECT 
		o.City || COALESCE(', ' || o.State, '') || COALESCE(', ' || o.Country, '') AS [location]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
)
GROUP BY [location]
ORDER BY [count] DESC
LIMIT 1
    """,
}

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Palm]:
    palms:list[Palm] = []
    print("Reading palms from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        palm = Palm()
        palm.id = None
        palm.legacy_id = row[0]
        palm.genus = clean(row[1])
        palm.species = clean(row[2])
        palm.variety = clean(row[3])
        palm.common_name = clean(row[4])
        palm.zone_name = clean(row[5])
        palm.zone_id = -1
        palms.append(palm)

    wb.close()
    return palms

def write_to_database(database_path:str, palms:list[Palm]) -> None:
    print("Inserting palms to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for palm in palms:
            # print(f"\tFinding zone {palm.ZoneName}")
            cur.execute(
                """
SELECT Id
FROM Zone
WHERE Zone.Name = ?
LIMIT 1
""",
                (palm.zone_name,),
            )
            result = cur.fetchone()
            if result is None:
                palm.zone_id = 0
            else:
                palm.zone_id = result[0]

            data = (
                palm.id,
                palm.legacy_id,
                palm.genus,
                palm.species,
                palm.variety,
                palm.common_name,
                palm.zone_id,
                palm.last_modified,
                palm.who_modified,
            )
            # print("\tPerforming insert...")
            cur.execute(
                "INSERT INTO Palm (Id, LegacyId, Genus, Species, Variety, CommonName, ZoneId, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while populating palms or inserting into sqlite.", error)
    finally:
        if con:
            con.close()
