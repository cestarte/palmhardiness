import openpyxl
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Optional
from util.string import clean, normalize_country, normalize_state, normalize_city
from data.models.location import Location
from geopy.geocoders import Nominatim

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
        "Country" varchar NOT NULL,
        "WhenAttemptedGeocode" timestamp
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
    location.when_attempted_geocode = row["WhenAttemptedGeocode"]

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

def read_locations_without_latlon(database_path:str) -> list[Location]:
    locations:list[Location] = []
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        long_ago = datetime.now(timezone.utc) - timedelta(days=30)
        # get all locations which don't have lat & lon
        # and have a country
        # and have not attempted geocoding in at since 'long_ago'
        cur.execute(
            """
            SELECT [Id], [City], [State], [Country]
            FROM Location
            WHERE ([Latitude] IS NULL 
                OR [Longitude] IS NULL)
                AND [Country] IS NOT NULL
                AND ([WhenAttemptedGeocode] IS NULL OR [WhenAttemptedGeocode] < ?)
            ORDER BY [Country] DESC, [State] DESC, [City] ASC
            """,
            (long_ago,),
        )
        rows:list[sqlite3.Row] = cur.fetchall()
        for row in rows:
            location = Location()
            location.id = row[0]
            location.city = row[1]
            location.state = row[2]
            location.country = row[3]
            #location.latitude = row[4]
            #location.longitude = row[5]
            #location.when_attempted_geocode = row[6]
            locations.append(location)
    except sqlite3.Error as error:
        print("Error while reading Locations from sqlite...", error)
    finally:
        if con:
            con.close()
    return locations

def update_latlon(database_path:str, location:Location) -> None:
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        data = (
            location.latitude,
            location.longitude,
            location.geo,
            location.when_attempted_geocode,
            location.who_modified,
            location.last_modified,
            location.id,
        )
        cur.execute(
            "UPDATE Location SET Latitude = ?, Longitude = ?, Geo = ?, WhenAttemptedGeocode = ?, WhoModified = ?, LastModified = ? WHERE Id = ?",
            data,
        )
        con.commit()
    except sqlite3.Error as error:
        print("Error while updating Latitude and Longitude in sqlite...", error)
    finally:
        if con:
            con.close()

def update_geocode_attempt(database_path:str, location:Location) -> None:
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        data = (
            location.when_attempted_geocode,
            location.who_modified,
            location.last_modified,
            location.id,
        )
        cur.execute(
            "UPDATE Location SET WhenAttemptedGeocode = ?, WhoModified = ?, LastModified = ? WHERE Id = ?",
            data,
        )
        con.commit()
    except sqlite3.Error as error:
        print("Error while updating Location geocode attempt date in sqlite...", error)
    finally:
        if con:
            con.close()

def populate_latlon(database_path:str, locations:list[Location]) -> None:
    """ Populate the Latitude and Longitude fields of the Location table by using Country, City, & State to geocode the address. 
    Use the geopy library to geocode the address via the Nominatim geocoder. """
    pass
    geolocator = Nominatim(user_agent="Palm Cold Hardiness 0.1")
    #location = geolocator.geocode("175 5th Avenue NYC")

    # read all the locations which don't already have lat & lon from the database
    current_index = 0
    for location in locations:
        current_index += 1
        print(f'Geocoding {current_index} of {len(locations)}')
        
        address = ''
        if location.city is not None:
            address += location.city
        if location.state is not None:
            if address != '':
                address += ', '
            address += location.state
        if location.country is not None:
            if address != '':
                address += ', '
            address += location.country
        print(f'  "{address}"')
   
        geocoded_location = None
        try:
            geocoded_location = geolocator.geocode(address)
        except Exception as e:
            print(f'  Error geocoding "{address}"', e)
        finally:
            location.when_attempted_geocode = datetime.now(timezone.utc)
            location.who_modified = 'Geocoder'
            location.last_modified = location.when_attempted_geocode 

        if geocoded_location is not None:
            location.latitude = geocoded_location.raw['lat']
            location.longitude = geocoded_location.raw['lon']
            location.geo = str(geocoded_location.raw)
            print(f'  {location.latitude}, {location.longitude}')
            update_latlon(database_path, location)
        else:
            print(f'  No location found.')
            update_geocode_attempt(database_path, location)

        # rate limit to avoid banning
        time.sleep(90) 



def populate_hrap(database_path:str):
    """ The US National Weather Service uses Hydrologic Rainfall Analysis Project (HRAP) grid to identify locations. 
    If a location is in the US, we can use the HRAP grid to consider rainfall data. """
    #if location.country.lower() != 'united states':
    #    continue
    pass