import openpyxl
import sqlite3
from util.string import clean
from data.models.cycad import Cycad
from data.queries.cycadqueries import queries

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Cycad]:
    cycads:list[Cycad] = []
    print("Reading cycads from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        if row[0] is None or row[0] == "":
            continue

        cycad = Cycad()
        cycad.id = None
        cycad.genus = clean(row[1])
        cycad.species = clean(row[2])
        cycad.variety = clean(row[3])
        cycad.common_name = clean(row[4])
        cycad.zone_name = clean(row[5])
        cycad.zone_id = -1



        if cycad.species == 'NULL':
            cycad.species = None
        if cycad.variety == 'NULL':
            cycad.variety = None
        if cycad.common_name == 'NULL':
            cycad.common_name = None

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
            data = (
                cycad.id,
                cycad.legacy_id,
                cycad.genus,
                cycad.species,
                cycad.variety,
                cycad.common_name,
                cycad.last_modified,
                cycad.who_modified,
            )
            # print("\tPerforming insert...")
            cur.execute(
                queries["insert"],
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while populating cycads or inserting into sqlite.", error)
    finally:
        if con:
            con.close()





