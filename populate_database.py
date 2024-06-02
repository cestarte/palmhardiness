import argparse
from data.repositories import zonerepo
from data.repositories import damagerepo
from data.repositories import synonymrepo
from data.repositories import eventrepo
from data.repositories import palmrepo
from data.repositories import palmsynonymrepo
from data.repositories import palmobservationrepo
from data.repositories import cycadrepo
from data.repositories import cycadobservationrepo


def main():
    parser = argparse.ArgumentParser(
        description="Import the cold hardiness master data to Sqlite."
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Specify the database full path. Default: PalmHardiness.db",
    )
    parser.add_argument(
        "-e",
        "--excel",
        help="Specify the excel file path.",
        required=True
    )

    database_path = "PalmHardiness.db"

    args = parser.parse_args()
    excel_path = args.excel
    if args.path:
        database_path = args.path
    
    zones = zonerepo.read_from_excel(excel_path, "Zones_tbl")
    zonerepo.write_to_database(database_path, zones)

    damages = damagerepo.read_from_excel(excel_path, "Damage_tbl")
    damagerepo.write_to_database(database_path, damages)

    synonyms = synonymrepo.read_from_excel(excel_path, "Synonyms_tbl")
    synonymrepo.write_to_database(database_path, synonyms)

    events = eventrepo.read_from_excel(excel_path, "Events_tbl", 3)
    eventrepo.write_to_database(database_path, events)

    palms = palmrepo.read_from_excel(excel_path, "Palms_tbl")
    palmrepo.write_to_database(database_path, palms)

    palmsynonymrepo.connect(database_path)

    palmobservations = palmobservationrepo.read_from_excel(excel_path, "HardinessPalms_tbl")
    palmobservations = palmobservationrepo.translate_ids(database_path, palmobservations)
    palmobservationrepo.write_to_database(database_path, palmobservations)    

    cycads = cycadrepo.read_from_excel(excel_path, "Cycads_tbl")
    cycadrepo.write_to_database(database_path, cycads)

    cycadobservations = cycadobservationrepo.read_from_excel(excel_path, "HardinessCycads_tbl")
    cycadobservations = cycadobservationrepo.translate_ids(database_path, cycadobservations)
    cycadobservationrepo.write_to_database(database_path, cycadobservations)    

if __name__ == "__main__":
    main()
