import openpyxl
import sqlite3
from util.string import clean
from data.models.palm import Palm

queries = {
    "get_count": """
SELECT COUNT(*) as count
FROM (
        WITH varCTE AS (SELECT ? AS varFilterObserved, UPPER(?) AS varTerm)
        SELECT COUNT(*) as ObservationCount
        FROM Palm, varCTE
        LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
        LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
        -- Allow unobserved unless we are filtering them out
        WHERE (PalmObservation.Id IS NOT NULL OR varFilterObserved = 0)
        -- If there is a search term, then filter on it
            AND (varTerm is NULL 
                OR INSTR(UPPER(Genus), varTerm) > 0 
                OR INSTR(UPPER(Species), varTerm) > 0 
                OR INSTR(UPPER(Variety), varTerm) > 0 
                OR INSTR(UPPER(CommonName), varTerm) > 0
                OR INSTR(UPPER(Zone.Name), varTerm) > 0
    )
    GROUP BY Palm.Id
)
    """,

    "get_records": """
WITH varCTE AS (SELECT ? AS varFilterObserved, UPPER(?) AS varTerm)
SELECT Palm.*
    ,Zone.Name as ZoneName
    ,COUNT(PalmObservation.Id) as ObservationCount
FROM Palm, varCTE
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
-- Allow unobserved unless we are filtering them out
WHERE (PalmObservation.Id IS NOT NULL OR varFilterObserved = 0)
-- If there is a search term, then filter on it
    AND (varTerm is NULL 
        OR INSTR(UPPER(Genus), varTerm) > 0 
        OR INSTR(UPPER(Species), varTerm) > 0 
        OR INSTR(UPPER(Variety), varTerm) > 0 
        OR INSTR(UPPER(CommonName), varTerm) > 0
        OR INSTR(UPPER(Zone.Name), varTerm) > 0
    )
GROUP BY Palm.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,


    "get_one": """
SELECT Palm.*
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
SELECT PalmObservation.*
    ,Palm.LegacyId as PalmLegacyId
    ,Palm.Genus as PalmGenus
    ,Palm.Species as PalmSpecies
    ,Palm.Variety as PalmVariety
    ,Palm.CommonName as PalmCommonName
    ,Palm.ZoneId as PalmZoneId
    ,Zone.Name as ZoneName
FROM PalmObservation
LEFT JOIN Palm ON PalmObservation.PalmId = Palm.Id
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
WHERE PalmObservation.PalmId = ?
ORDER BY PalmObservation.ObservationDate DESC
    """,

}

def read_from_row(row:sqlite3.Row) -> Palm:
    palm = Palm()
    palm.id = row["Id"]
    palm.legacy_id = row["LegacyId"]
    palm.genus = row["Genus"]
    palm.species = row["Species"]
    palm.variety = row["Variety"]
    palm.common_name = row["CommonName"]
    palm.zone_id = row["ZoneId"]
    palm.last_modified = row["LastModified"]
    palm.who_modified = row["WhoModified"]
    if hasattr(palm, 'zone_name') and 'ZoneName' in row.keys():
        palm.zone_name = row["ZoneName"]
    if hasattr(palm, 'observation_count') and 'ObservationCount' in row.keys():
        palm.observation_count = row["ObservationCount"]
    return palm

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
