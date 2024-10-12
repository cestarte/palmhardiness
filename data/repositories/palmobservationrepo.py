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
        i.legacy_id = row[0]
        i.palm_id = None
        i.palm_legacy_id = row[1]
        i.damage_id = None
        i.damage_legacy_id = row[7]
        i.event_id = None
        i.event_legacy_id = row[10]
        i.who_reported = clean(row[2])
        i.city = clean(row[3])
        i.state = clean(row[4])
        i.country = clean(row[5])
        i.low_temp = row[6]
        i.description = clean(row[8])
        i.source = clean(row[9])

        if '2023' in workbook and i.legacy_id == 4912 and i.event_id == None:
            print("[WARNING] Correcting for single 2023 observation missing event id")
            i.event_legacy_id = 85

        items.append(i)

    wb.close()
    return items


def translate_ids(database_path:str, observations:list[PalmObservation]) -> list[PalmObservation]:
    """Populate the relationship ids on the observation. To do that, use the 
    excel legacy ids to look up the id in our database."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            # Find the database's palm Id by using the legacy id from the Excel
            cur.execute(
                palmqueries["select_by_legacy_id"],
                (o.palm_legacy_id,),
            )
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching palm for legacy id {o.palm_legacy_id}. Skipping..."
                )
                continue
            else:
                o.palm_id = result[0]

            # Find the database's event Id by using the legacy id from the Excel
            # Note: 0 in the Excel means no event recorded
            if o.event_legacy_id != 0:
                cur.execute(
                    eventqueries["select_by_legacy_id"],
                    (o.event_legacy_id,),
                )
                result = cur.fetchone()
                if result is None:
                    print(
                        f"[WARNING] Couldn't find a matching event for legacy id {o.event_legacy_id}. Skipping..."
                    )
                    print("The item", vars(o))
                    continue
                else:
                    o.event_id = result[0]

            # Find the database's damage Id by using the legacy Id from the Excel
            cur.execute(
                damagequeries['select_by_legacy_id'],
                (o.damage_legacy_id,),
            )
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching damage for LegacyId {o.damage_legacy_id}. Skipping..."
                )
                print("The item", vars(o))
                continue
            else:
                o.damage_id = result[0]

    except sqlite3.Error as error:
        print("[ERROR] Failed while populating observation relations from sqlite.", error)
    finally:
        if con:
            con.close()

    return observations


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
                o.legacy_id,
                o.palm_id,
                o.palm_legacy_id,
                o.who_reported,
                o.city,
                o.state,
                o.country,
                o.damage_id,
                o.damage_legacy_id,
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


def read_from_row(row:sqlite3.Row) -> PalmObservation:
    o = PalmObservation()
    o.id = row['Id']
    o.legacy_id = row['LegacyId']
    o.palm_id = row['PalmId']
    o.palm_legacy_id = row['PalmLegacyId']
    o.who_reported = row['WhoReported']
    o.city = row['City']
    o.state = row['State']
    o.country = row['Country']
    o.damage_id = row['DamageId']
    o.damage_legacy_id = row['DamageLegacyId']
    o.event_id = row['EventId']
    o.event_legacy_id = row['EventLegacyId']
    o.description = row['Description']
    o.source = row['Source']
    o.low_temp = row['LowTemp']
    o.last_modified = row['LastModified']
    o.who_modified = row['WhoModified']
    o.location_id = row['LocationId']

    # These are the joined fields
    o.event_name = row['EventName']
    o.event_description = row['EventDescription']
    o.event_who_reported = row['EventWhoReported']
    o.damage_text = row['DamageText']

    return o