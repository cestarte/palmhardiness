import openpyxl
from datetime import datetime
import sqlite3

class Event:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int | None = None
        self.who_reported:str = "Unknown"
        self.city:str = "Unknown"
        self.state:str = "Unknown"
        self.country:str = "Unknown"
        self.name:str = "Unknown"
        self.description:str = "Unknown"
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Event]:
    events:list[Event] = []
    print("Reading events from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        event = Event()
        event.id = None
        event.legacy_id = row[0]
        event.who_reported = row[1]
        event.city = row[2]
        event.state = row[3]
        event.country = row[4]
        event.name = row[5]
        event.description = row[6]
        events.append(event)

    wb.close()
    return events


def write_to_database(database_path:str, events:list[Event]) -> None:
    print("Inserting events to database...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for event in events:
            data = (
                event.id,
                event.legacy_id,
                event.who_reported,
                event.city,
                event.state,
                event.country,
                event.name,
                event.description,
                event.last_modified,
                event.who_modified,
            )
            cur.execute(
                "INSERT INTO Event (Id, LegacyId, WhoReported, City, State, Country, Name, Description, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting events into sqlite.", error)
    finally:
        if con:
            con.close()
