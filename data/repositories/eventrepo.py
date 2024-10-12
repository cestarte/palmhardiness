import openpyxl
import sqlite3
from util.string import clean, normalize_country, normalize_state, normalize_city, remove_underscore
from data.models.event import Event
from data.queries.eventqueries import queries
from typing import Optional

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Event]:
    events:list[Event] = []
    print("Reading events from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        event = Event()
        event.id = None
        event.legacy_id = row[0]
        event.who_reported = clean(row[1])
        event.city = clean(row[2])
        event.state = clean(row[3])
        event.country = clean(row[4])
        event.name = remove_underscore(clean(row[5]))
        event.description = clean(row[6])
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
                queries['insert'],
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting events into sqlite.", error)
    finally:
        if con:
            con.close()

def read_from_row(row:sqlite3.Row) -> Event:
    event = Event()
    event.id = row['Id']
    event.legacy_id = row['LegacyId']
    event.city = row['City']
    event.state = row['State']
    event.country = row['Country']
    event.name = row['Name']
    event.description = row['Description']
    event.who_reported = row['WhoReported']
    event.last_modified = row['LastModified']
    event.who_modified = row['WhoModified']
    event.location_id = row['LocationId']

    # Joined fields
    if 'Latitude' in row.keys():
        event.latitude = row['Latitude']
    if 'Longitude' in row.keys():
        event.longitude = row['Longitude']
    if 'Geo' in row.keys():
        event.geo = row['Geo']

    return event