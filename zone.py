import openpyxl
from datetime import datetime
import sqlite3

class Zone:
    def __init__(self):
        self.id:int | None = None
        self.name:str = "Unknown"
        self.min:float = -1.0
        self.max:float = 1.0
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Zone]:
    zones:list[Zone] = []
    print("Reading zones from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        zone = Zone()
        zone.name = row[0]
        zone.min = row[1]
        zone.max = row[2]
        zones.append(zone)

    wb.close()
    return zones

def write_to_database(database_path:str, zones:list[Zone]) -> None:
    print("Inserting zones to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        # zones[1].print()

        for zone in zones:
            data = (
                zone.id,
                zone.name,
                zone.min,
                zone.max,
                zone.last_modified,
                zone.who_modified,
            )
            cur.execute(
                "INSERT INTO Zone (Id, Name, MinTempF, MaxTempF, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting zones into sqlite.", error)
    finally:
        if con:
            con.close()
