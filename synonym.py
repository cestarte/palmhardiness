import openpyxl
from datetime import datetime
import sqlite3

class Synonym:
    def __init__(self):
        self.id:int | None = None
        self.palm_legacy_id:int | None = None
        self.genus:str = "Unknown"
        self.species:str = "Unknown"
        self.variety:str = "Unknown"
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

def read_from_excel(workbook:str, sheet:str, first_row_with_data:int=2) -> list[Synonym]:
    items:list[Synonym] = []
    print("Reading synonyms from spreadsheet...", sheet)
    wb = openpyxl.load_workbook(workbook)
    ws = wb[sheet]

    for row in ws.iter_rows(min_row=first_row_with_data, values_only=True):
        item = Synonym()
        item.palm_legacy_id = row[0]
        item.genus = row[1]
        item.species = row[2]
        item.variety = row[3]
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
                "INSERT INTO Synonym (Id, PalmLegacyId, Genus, Species, Variety, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?)",
                data,
            )
        con.commit()
    except sqlite3.Error as error:
        print("Error while inserting synonyms into sqlite.", error)
    finally:
        if con:
            con.close()


# run connect after both synonyms & palms have been written to db
def connect(database_path:str) -> None:
    """Connect palm synonym relationships."""
    try:
        con = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        cur = con.cursor()
        cur.execute(
            """
INSERT INTO PalmSynonym (PalmId, SynonymId)
SELECT * FROM (
	SELECT 
		S.Id AS SynonymId
		,P.Id AS PalmId
	FROM Synonym AS S
	INNER JOIN Palm AS P ON S.PalmLegacyId = P.LegacyId
)

""",
        )
        con.commit()

    except sqlite3.Error as error:
        print("Error while connecting synonyms in sqlite.", error)
    finally:
        if con:
            con.close()
