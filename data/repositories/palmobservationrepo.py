import openpyxl
import sqlite3
from util.string import clean
from data.models.palmobservation import PalmObservation
from data.queries.palmobservationqueries import queries
from data.queries.palmqueries import queries as palmqueries
from data.queries.eventqueries import queries as eventqueries
from data.queries.damagequeries import queries as damagequeries

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int = 2) -> list[PalmObservation]:
    items:list[PalmObservation] = []
    print("Reading palm hardiness observations from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row = first_row_with_data, values_only = True):
        i = PalmObservation()
        i.id = None
        i.palm_id = None
        i.genus = clean(row[0])
        i.species = clean(row[1])
        i.variety = clean(row[2])

        i.damage_text = clean(row[10])
        i.damage_id = None
        i.event_id = None
        # Convert event_legacy_id to int
        try:
            raw_value = row[11]
            if raw_value is None or raw_value == "":
                i.event_legacy_id = 0
            elif isinstance(raw_value, (int, float)):
                i.event_legacy_id = int(raw_value)
            elif isinstance(raw_value, str) and raw_value.strip().isdigit():
                i.event_legacy_id = int(raw_value.strip())
            else:
                # default to 0
                i.event_legacy_id = 0
        except (ValueError, TypeError, AttributeError):
            i.event_legacy_id = 0  # Default to 0 if conversion fails
        i.who_reported = clean(row[5])
        i.city = clean(row[6])
        i.state = clean(row[7])
        i.country = clean(row[8])
        i.low_temp = row[9]
        i.description = clean(row[12])
        i.source = clean(row[13])

        items.append(i)

    wb.close()
    return items

def translate_ids(database_path:str, observations:list[PalmObservation]) -> list[PalmObservation]:
    """Use information we have to connect relationships with other tables."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            # Find the database's palm Id by using the genus, species, and variety
            cur.execute(palmqueries["select_by_genus_species_variety"], 
                        (o.genus, o.species, o.variety,),)
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching palm for '{o.genus}', '{o.species}', '{o.variety}'. This observation will not be included."
                )
                continue
            else:
                o.palm_id = result[0]

            # Find the database's damage Id by using the text
            cur.execute(
                damagequeries['select_by_text'],
                (o.damage_text,),
            )
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching damage for text {o.damage_text}. This observation will not be included."
                )
                print("The item", vars(o))
                continue
            else:
                o.damage_id = result[0]

            # Find the database's event Id by using the legacy id (from the Excel)
            # Note: 0 in the Excel means no event recorded
            if o.event_legacy_id is not None and o.event_legacy_id != 0:
                cur.execute(
                    eventqueries["select_by_legacy_id"],
                    (o.event_legacy_id,),
                )
                result = cur.fetchone()
                if result is None:
                    print(
                        f"[WARNING] Couldn't find a matching event for legacy id {o.event_legacy_id}. This observation will not be tied to an event."
                    )
                    print("The item", vars(o))
                else:
                    o.event_id = result[0]

    except sqlite3.Error as error:
        print("[ERROR] Failed while populating observation relations from sqlite.", error)
    finally:
        if con:
            con.close()

    return [o for o in observations if o.damage_id is not None and o.palm_id is not None]


def write_to_database(database_path:str, observations:list[PalmObservation]) -> None:
    print("Inserting palmobservations to database...")
    current_observation:PalmObservation | None = None
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            current_observation = o
            data = (
                o.palm_id,
                o.who_reported,
                o.city,
                o.state,
                o.country,
                o.damage_id,
                o.event_legacy_id,
                o.event_id,
                o.description,
                o.source,
                o.low_temp,
                o.last_modified,
                o.who_modified,
            )

            cur.execute(
                queries["insert"],
                data,
            )
            con.commit()
    except sqlite3.Error as error:
        print("[ERROR] Failed while inserting observations into sqlite.", error)
        if current_observation is not None and isinstance(current_observation, PalmObservation):
            print("Here's the observation which caused the error:", vars(current_observation))
    finally:
        if con:
            con.close()
