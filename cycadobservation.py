import openpyxl
from datetime import datetime
import sqlite3

class CycadObservation:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int
        self.cycad_id:int
        self.cycad_legacy_id:int
        self.who_reported:str
        self.city:str | None = None
        self.state:str | None = None
        self.country:str
        self.damage_id:int
        self.damage_legacy_id:int
        self.event_legacy_id:int
        self.event_id:int
        self.description:str
        self.source:str
        self.low_temp:float
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"


def read_from_excel(workbook:str, sheet:str, first_row_with_data:int = 2) -> list[CycadObservation]:
    items:list[CycadObservation] = []
    print("Reading cycad hardiness observations from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row = first_row_with_data, values_only = True):
        i = CycadObservation()
        i.id = None
        i.legacy_id = row[0]
        i.cycad_id = None
        i.cycad_legacy_id = row[1]
        i.damage_id = None
        i.damage_legacy_id = row[7]
        i.event_id = None
        i.event_legacy_id = row[10]
        i.who_reported = row[2]
        i.city = row[3]
        i.state = row[4]
        i.country = row[5]
        i.low_temp = row[6]
        i.description = row[8]
        i.source = row[9]
        
        if '2023' in workbook and i.legacy_id == 71 and i.event_id == None:
            print("[WARNING] Correcting for single 2023 observation missing event id")
            i.event_legacy_id = 85

        items.append(i)

    wb.close()
    return items


def translate_ids(database_path:str, observations:list[CycadObservation]) -> list[CycadObservation]:
    """Populate the relationship ids on the observation. To do that, use the 
    excel legacy ids to look up the id in our database."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()

        for o in observations:
            # Find the database's cycad Id by using the legacy id from the Excel
            cur.execute(
                """
SELECT Id
FROM Cycad
WHERE LegacyId = ?
LIMIT 1
""",
                (o.cycad_legacy_id,),
            )
            result = cur.fetchone()
            if result is None:
                print(
                    f"[WARNING] Couldn't find a matching cycad for legacy id {o.cycad_legacy_id}. Skipping..."
                )
                continue
            else:
                o.cycad_id = result[0]

            # Find the database's event Id by using the legacy id from the Excel
            # Note: 0 in the Excel means no event recorded
            if o.event_legacy_id != 0:
                cur.execute(
                    """
SELECT Id
FROM Event
WHERE LegacyId = ?
LIMIT 1
                """,
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
                """
SELECT Id
FROM Damage
WHERE LegacyId = ?
LIMIT 1
""",
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


def write_to_database(database_path:str, observations:list[CycadObservation]):
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
                o.legacy_id,
                o.cycad_id,
                o.cycad_legacy_id,
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
                "INSERT INTO CycadObservation (LegacyId, CycadId, CycadLegacyId, WhoReported, City, State, Country, DamageId, DamageLegacyId, EventId, EventLegacyId, Description, Source, LowTemp, LastModified, WhoModified) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
