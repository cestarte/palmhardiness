import argparse
import zone
import damage
import synonym
import event
import palm
import palmobservation
import cycad
import cycadobservation

def main():
    parser = argparse.ArgumentParser(
        description="Import the cold hardiness master data to Sqlite."
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Specify the database full path. Default: PalmTalk.db",
    )
    parser.add_argument(
        "-e",
        "--excel",
        help="Specify the excel file path.",
        required=True
    )

    database_path = "PalmTalk.db"

    args = parser.parse_args()
    excel_path = args.excel
    if args.path:
        database_path = args.path
    
    zones = zone.read_from_excel(excel_path, "Zones_tbl")
    zone.write_to_database(database_path, zones)

    damages = damage.read_from_excel(excel_path, "Damage_tbl")
    damage.write_to_database(database_path, damages)

    synonyms = synonym.read_from_excel(excel_path, "Synonyms_tbl")
    synonym.write_to_database(database_path, synonyms)

    events = event.read_from_excel(excel_path, "Events_tbl", 3)
    event.write_to_database(database_path, events)

    palms = palm.read_from_excel(excel_path, "Palms_tbl")
    palm.write_to_database(database_path, palms)

    synonym.connect(database_path)

    palmobservations = palmobservation.read_from_excel(excel_path, "HardinessPalms_tbl")
    palmobservations = palmobservation.translate_ids(database_path, palmobservations)
    palmobservation.write_to_database(database_path, palmobservations)    

    cycads = cycad.read_from_excel(excel_path, "Cycads_tbl")
    cycad.write_to_database(database_path, cycads)

    cycadobservations = cycadobservation.read_from_excel(excel_path, "HardinessCycads_tbl")
    cycadobservations = cycadobservation.translate_ids(database_path, cycadobservations)
    cycadobservation.write_to_database(database_path, cycadobservations)    

if __name__ == "__main__":
    main()
