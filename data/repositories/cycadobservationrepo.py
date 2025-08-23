import openpyxl
import sqlite3
from util.string import clean
from data.models.cycadobservation import CycadObservation
from data.queries.cycadobservationqueries import queries
from data.queries.cycadqueries import queries as cycadqueries
from data.queries.damagequeries import queries as damagequeries
from data.queries.eventqueries import queries as eventqueries

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int = 2) -> list[CycadObservation]:
    """ Read cycad observations from an Excel spreadsheet. """
    items:list[CycadObservation] = []
    print("Reading cycad hardiness observations from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row = first_row_with_data, values_only = True):
        if row[0] is None or str(row[0]).strip() == "":
            continue

        i = CycadObservation()
        i.id = None
        i.cycad_id = None
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

def translate_ids(database_path:str, observations:list[CycadObservation]) -> list[CycadObservation]:
    """Populate Event & Damage relationship ids on the observation. To do that, 
    use the excel legacy ids to look up the id in our database."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            # Find the database's cycad Id  by using the genus, species, and variety
            cur.execute(
                cycadqueries["select_by_genus_species_variety"],
                (o.genus, o.species, o.variety,),
            )
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching cycad for '{o.genus}', '{o.species}', '{o.variety}'. Skipping..."
                )
                continue
            else:
                o.cycad_id = result[0]


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

    return observations

def write_to_database(database_path:str, observations:list[CycadObservation]):
    """Insert cycad observations into the database."""
    print("Inserting cycadobservations to database...")
    current_observation:CycadObservation | None = None
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            current_observation = o
            data = (
                o.cycad_id,
                o.who_reported,
                o.city,
                o.state,
                o.country,
                o.damage_id,
                o.event_id,
                o.event_legacy_id,
                o.description,
                o.source,
                o.low_temp,
                o.last_modified,
                o.who_modified,
            )

            cur.execute(
                "INSERT INTO CycadObservation (CycadId, WhoReported, City, State, Country, DamageId, EventId, EventLegacyId, Description, Source, LowTemp, LastModified, WhoModified) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                data,
            )
            con.commit()
    except sqlite3.Error as error:
        print("[ERROR] Failed while inserting observations into sqlite.", error)
        if current_observation is not None and isinstance(current_observation, CycadObservation):
            print("Here's the observation which caused the error:", vars(current_observation))
    finally:
        if con:
            con.close()
