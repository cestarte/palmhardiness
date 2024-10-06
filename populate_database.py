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
from data.repositories import locationrepo

def main():
    parser = argparse.ArgumentParser(
        description="Import the cold hardiness master data to Sqlite."
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Specify the database full path. Default: PalmHardiness.db",
        default="PalmHardiness.db",
        required=False
    )
    parser.add_argument(
        "-e",
        "--excel",
        help="Specify the excel file path.",
        required=False
    )
    parser.add_argument(
        "-l",
        "--location",
        help="Geolocate locations in the database.",
        action="store_true",
        required=False
    )

    args = parser.parse_args()

    if args.excel is not None:
        perform_import(args.excel, args.database)
    
    if args.location:
        locationrepo.populate_latlon(args.database)
        locationrepo.populate_hrap(args.database)
    

def perform_import(excel_path, database_path):
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

    locations = locationrepo.read_locations_from_other_tables(database_path)
    non_locations = [x for x in locations if x.country == None]
    if len(non_locations) > 0:
        print(f'WARNING: Found useless locations with no country.')
        print('These will not be inserted into the database:')
        print([str(x) for x in non_locations]) 
    locationrepo.write_to_database_and_wire_up(database_path, [x for x in locations if x.country != None])
    
    #locationrepo.geolocate(database_path)
    #locationrepo.populate_hrap(database_path)

if __name__ == "__main__":
    main()
