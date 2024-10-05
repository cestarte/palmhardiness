import openpyxl
import sqlite3
from typing import Optional
from util.string import clean, normalize_country, normalize_state, normalize_city
from data.models.location import Location

queries = {
    "drop": """
DROP TABLE IF EXISTS "Location"
    """,
    "create": """
        CREATE TABLE IF NOT EXISTS "Location" (
        "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
        "LastModified" timestamp NOT NULL,
        "WhoModified" varchar(128) NOT NULL,
        "Latitude" varchar(6),
        "Longitude" varchar(6),
        "City" varchar(512),
        "State" varchar(512),
        "Country" varchar NOT NULL
        );
    """,

    "get_records": """
        WITH vars AS (SELECT UPPER(?) AS term)
        SELECT 
            Location.*
            ,(SELECT COUNT(PalmObservation.Id) FROM PalmObservation WHERE PalmObservation.LocationId = Location.Id) AS PalmObservations
            ,(SELECT COUNT(CycadObservation.Id) FROM CycadObservation WHERE CycadObservation.LocationId = Location.Id) AS CycadObservations
            ,(SELECT COUNT(Event.Id) FROM Event WHERE Event.LocationId = Location.Id) AS Events
        FROM Location, vars
        WHERE (vars.term IS NULL 
            OR INSTR(UPPER(Location.City), vars.term) > 0 
            OR INSTR(UPPER(Location.State), vars.term) > 0 
            OR INSTR(UPPER(Location.Country), vars.term) > 0
        )
        ORDER BY Location.Country, Location.State, Location.City
        LIMIT ? OFFSET ?
    """,

    "get_count": """
        WITH vars AS (SELECT UPPER(?) AS term)
        SELECT COUNT(*) FROM Location, vars
        WHERE (term IS NULL 
            OR INSTR(UPPER(City), term) > 0 
            OR INSTR(UPPER(State), term) > 0 
            OR INSTR(UPPER(Country), term) > 0
        )
    """,
}

def read_from_row(row:sqlite3.Row) -> Location:
    #print("row", row.keys())
    location = Location()
    location.id = row["Id"]
    location.last_modified = row["LastModified"]
    location.who_modified = row["WhoModified"]
    location.latitude = row["Latitude"]
    location.longitude = row["Longitude"]
    location.city = row["City"]
    location.state = row["State"]
    location.country = row["Country"]

    # Fields not in the Location table
    print("CycadObservations", row["CycadObservations"])
    if row["CycadObservations"] is not None:
        location.cycad_observations = row["CycadObservations"]
    print("PalmObservations", row["PalmObservations"])
    if row["PalmObservations"] is not None:
        location.palm_observations = row["PalmObservations"]
    print("Events", row["Events"])
    if row["Events"] is not None:
        location.events = row["Events"]
    return location

def read_locations_from_other_tables(database_path:str) -> list[Location]:
    locations:list[Location] = []
    print("Reading location fields from observation & event tables...")
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        cur.execute(
            """
            SELECT [City], [State], [Country], [Id] AS [SourceId], 'event' AS [Source]
            FROM Event 
            UNION 
            SELECT [City], [State], [Country], [Id] AS [SourceId], 'palm' AS [Source]
            FROM PalmObservation 
            UNION 
            SELECT [City], [State], [Country], [Id] AS [SourceId], 'cycad' AS [Source]
            FROM CycadObservation
            """
        )
        rows = cur.fetchall()
        for row in rows:
            location = Location()
            location.city = normalize_city(row[0])
            location.state = normalize_state(row[1])
            location.country = normalize_country(row[2])
            location.who_modified = "Importer"
            location.source_id = row[3]
            location.source = row[4]
            locations.append(location)
    except sqlite3.Error as error:
        print("Error while reading location fields from sqlite observation & event tables...", error)
    finally:
        if con:
            con.close()
    return locations

def write_to_database_and_wire_up(database_path:str, locations:list[Location]) -> None:
    print("Writing locations to database and wiring up foreign keys...")
    num_new_locations = 0
    num_events_updated = 0
    num_palm_observations_updated = 0
    num_cycad_observations_updated = 0

    for location in locations:
        existing_location_id = does_location_exist(database_path, location.country, location.state, location.city)
        if existing_location_id is not None: 
            # this location is already in the db
            location.id = existing_location_id
        else:
            # this is a new location record
            num_new_locations += 1
            new_record_id = write_to_database(database_path, location)
            location.id = new_record_id

        # Now add the foreign key to the record referencing this Location
        table_name = ''
        if location.source.lower() == 'event':
            table_name = 'Event'
            num_events_updated += 1
        elif location.source.lower() == 'palm':
            table_name = 'PalmObservation'
            num_palm_observations_updated += 1
        elif location.source.lower() == 'cycad':
            table_name = 'CycadObservation'
            num_cycad_observations_updated += 1
        else:
            raise Exception(f'Unknown source: {location.source}')

        update_foreign_key(database_path, table_name, location)

    print(f'# locations scanned: {len(locations)}')
    print(f'# new locations added: {num_new_locations}')
    print(f'Events updated: {num_events_updated}')
    print(f'PalmObservations updated: {num_palm_observations_updated}')
    print(f'CycadObservations updated: {num_cycad_observations_updated}')
            
def update_foreign_key(database_path:str, table_name:str, location:Location) -> None:
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        data = (
            location.id,
            location.source_id
        )
        cur.execute(
            f"""UPDATE {table_name} SET LocationId = ? WHERE Id = ?""",
            data,
        )
        con.commit()
        return cur.lastrowid
    except sqlite3.Error as error:
        print(f"Error while updating foreign key of Location form sqlite table '{table_name}'...", error)
    finally:
        if con:
            con.close()

def write_to_database(database_path:str, location:Location) -> int:
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        data = (
            location.last_modified,
            location.who_modified,
            location.latitude,
            location.longitude,
            location.city,
            location.state,
            location.country
        )
        cur.execute(
            "INSERT INTO Location (LastModified, WhoModified, Latitude, Longitude, City, State, Country) VALUES(?, ?, ?, ?, ?, ?, ?)",
            data,
        )
        con.commit()
        return cur.lastrowid
    except sqlite3.Error as error:
        print("Error while reading location fields from sqlite observation & event tables...", error)
    finally:
        if con:
            con.close()

def does_location_exist(database_path:str, country:Optional[str], state:Optional[str], city:Optional[str]) -> Optional[int]:
    country = normalize_country(country)
    state = normalize_state(state)
    city = normalize_city(city)

    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        cur.execute("SELECT * FROM Location WHERE Country IS ? AND State IS ? AND City IS ?", (country, state, city))
        result = cur.fetchone()
        return result[0] if result is not None else None
    except sqlite3.Error as error:
        print("Error while checking if Location table exists in sqlite.", error)
    finally:
        if con:
            con.close()
    return None
