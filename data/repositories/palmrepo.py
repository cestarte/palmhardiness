import openpyxl
import sqlite3
from util.string import clean
from data.models.palm import Palm
from data.queries.palmqueries import queries

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
            data = (
                palm.id,
                palm.legacy_id,
                palm.genus,
                palm.species,
                palm.variety,
                palm.common_name,
                palm.last_modified,
                palm.who_modified,
            )
            # print("\tPerforming insert...")
            cur.execute(
                queries["insert"],
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while populating palms or inserting into sqlite.", error)
    finally:
        if con:
            con.close()
