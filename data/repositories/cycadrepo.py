import openpyxl
import sqlite3
from util.string import clean
from data.models.cycad import Cycad

queries = {
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
    """
}

def read_from_row(row:sqlite3.Row) -> Cycad:
    cycad = Cycad()
    cycad.id = row["Id"]
    cycad.legacy_id = row["LegacyId"]
    cycad.genus = row["Genus"]
    cycad.species = row["Species"]
    cycad.variety = row["Variety"]
    cycad.common_name = row["CommonName"]
    cycad.zone_id = row["ZoneId"]
    cycad.last_modified = row["LastModified"]
    cycad.who_modified = row["WhoModified"]
    if hasattr(cycad, 'zone_name') and 'ZoneName' in row.keys():
        cycad.zone_name = row["ZoneName"]
    if hasattr(cycad, 'observation_count') and 'ObservationCount' in row.keys():
        cycad.observation_count = row["ObservationCount"]
    return cycad

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Cycad]:
    cycads:list[Cycad] = []
    print("Reading cycads from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        cycad = Cycad()
        cycad.id = None
        cycad.legacy_id = row[0]
        cycad.genus = clean(row[1])
        cycad.species = clean(row[2])
        cycad.variety = clean(row[3])
        cycad.common_name = clean(row[4])
        cycad.zone_name = clean(row[5])
        cycad.zone_id = -1

        if '2023' in workbook and cycad.legacy_id == 8025 and cycad.genus is None:
            print("[WARNING] Correcting for empty entry in 2023 spreadsheet. Ignoring row w/ id 8025")
            continue

        if '2024' in workbook and cycad.genus is None:
            print("[WARNING] Ignoring entry with missing genus in 2024 spreadsheet. Ignoring row w/ id", cycad.legacy_id)
            continue

        cycads.append(cycad)

    wb.close()
    return cycads


def write_to_database(database_path:str, cycads:list[Cycad]) -> None:
    print("Inserting cycads to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for cycad in cycads:
            # print(f"\tFinding zone {cycad.ZoneName}")
            cur.execute(
                """
SELECT Id
FROM Zone
WHERE Zone.Name = ?
LIMIT 1
""",
                (cycad.zone_name,),
            )
            result = cur.fetchone()
            if result is None:
                cycad.zone_id = 0
            else:
                cycad.zone_id = result[0]

            data = (
                cycad.id,
                cycad.legacy_id,
                cycad.genus,
                cycad.species,
                cycad.variety,
                cycad.common_name,
                cycad.zone_id,
                cycad.last_modified,
                cycad.who_modified,
            )
            # print("\tPerforming insert...")
            cur.execute(
                "INSERT INTO Cycad (Id, LegacyId, Genus, Species, Variety, CommonName, ZoneId, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while populating cycads or inserting into sqlite.", error)
    finally:
        if con:
            con.close()





