import openpyxl
from datetime import datetime
import sqlite3
import zone

class Palm:
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
