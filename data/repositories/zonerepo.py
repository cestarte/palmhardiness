import openpyxl
import sqlite3
from util.string import clean
from data.models.zone import Zone
from data.queries.zonequeries import queries

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Zone]:
    zones:list[Zone] = []
    print("Reading zones from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        zone = Zone()
        zone.name = clean(row[0])
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
                queries['insert'],
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting zones into sqlite.", error)
    finally:
        if con:
            con.close()

