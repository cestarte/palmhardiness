import openpyxl
from datetime import datetime
import sqlite3

class Damage:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int | None = None
        self.text:str = "Unknown"
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Damage]:
    damages:list[Damage] = []
    print("Reading damages from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(first_row_with_data, None):
        damage = Damage()
        damage.legacy_id = row[0].value
        damage.text = row[1].value
        damages.append(damage)

    wb.close()
    return damages

def write_to_database(database_path:str, damages:list[Damage]) -> None:
    print("Inserting damages to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for damage in damages:
            data = (
                damage.id,
                damage.legacy_id,
                damage.text,
                damage.last_modified,
                damage.who_modified,
            )
            cur.execute(
                "INSERT INTO Damage (Id, LegacyId, Text, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting damages into sqlite.", error)
    finally:
        if con:
            con.close()
