import openpyxl
import sqlite3
from util.string import clean
from data.models.synonym import Synonym
from data.queries.synonymqueries import queries

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Synonym]:
    items:list[Synonym] = []
    print("Reading synonyms from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        item = Synonym()
        item.palm_legacy_id = row[0]
        item.genus = clean(row[1])
        item.species = clean(row[2])
        item.variety = clean(row[3])
        items.append(item)

        item2 = Synonym()
        item2.palm_legacy_id = row[4]
        item2.genus = item.genus
        item2.species = item.species
        item2.variety = item.variety
        if item2.palm_legacy_id is not None:
            items.append(item2)

    wb.close()
    return items

def write_to_database(database_path:str, synonyms:list[Synonym]) -> None:
    print("Inserting synonyms to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for item in synonyms:
            data = (
                item.id,
                item.palm_legacy_id,
                item.genus,
                item.species,
                item.variety,
                item.last_modified,
                item.who_modified,
            )
            cur.execute(
                queries['insert'],
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting synonyms into sqlite.", error)
    finally:
        if con:
            con.close()

