import openpyxl
import sqlite3
from data.models.palm import Palm

queries = {
    "get_count": """
SELECT COUNT(*) as count
FROM Palm
    """,
    "get_all": """
SELECT Palm.*
    ,Zone.Name as ZoneName
FROM Palm
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,
    "get_one": """
SELECT Palm.*
    ,Zone.Name as ZoneName
FROM Palm
WHERE Id = ?
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
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
    """
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
    return palm

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Palm]:
    palms:list[Palm] = []
    print("Reading palms from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row_cells in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        palm = Palm()
        palm.id = None
        palm.legacy_id = row_cells[0]
        palm.genus = row_cells[1]
        palm.species = row_cells[2]
        palm.variety = row_cells[3]
        palm.common_name = row_cells[4]
        palm.zone_name = row_cells[5]
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
