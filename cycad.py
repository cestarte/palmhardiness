import openpyxl
from datetime import datetime
import sqlite3
import zone

class Cycad:
    def __init__(self):
        self.id = None
        self.legacy_id = None
        self.genus = None
        self.species = None
        self.variety = None
        self.common_name = None
        self.zone_id = 0
        self.zone_name = None
        self.last_modified = datetime.now()
        self.who_modified = "Excel Importer"

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Cycad]:
    cycads:list[Cycad] = []
    print("Reading cycads from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        cycad = Cycad()
        cycad.id = None
        cycad.legacy_id = row[0]
        cycad.genus = row[1]
        cycad.species = row[2]
        cycad.variety = row[3]
        cycad.common_name = row[4]
        cycad.zone_name = row[5]
        cycad.zone_id = -1

        if '2023' in workbook and cycad.legacy_id == 8025 and cycad.genus is None:
            print("[WARNING] Correcting for empty entry in 2023 spreadsheet. Ignoring row w/ id 8025")
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
