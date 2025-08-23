import sqlite3
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

def drop_tables(database_path):
    drop_queries = [
        ("Cycad Observation", cycadobservationrepo.queries['drop']),
        ("Cycad", cycadrepo.queries['drop']),
        ("Palm Synonym", palmsynonymrepo.queries['drop']),
        ("PalmObservation", palmobservationrepo.queries['drop']),
        ("Palm", palmrepo.queries['drop']),
        ("Damage", damagerepo.queries['drop']),
        ("Event", eventrepo.queries['drop']),
        ("Synonym", synonymrepo.queries['drop']),
        ("Zone", zonerepo.queries['drop']),
        #("Location", locationrepo.queries['drop']),
        ("palm views", palmrepo.queries['drop_views']),
    ]

    print("Dropping tables...")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        for query in drop_queries:
            print("\t" + query[0])
            cur.executescript(query[1])
            con.commit()
    except sqlite3.Error as error:
        print("Error while deleting tables from sqlite", error)
    finally:
        if con:
            con.close()
    print("...done.")

def drop_location_table(database_path):
    print("Dropping Location table...")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        cur.executescript(locationrepo.queries['drop'])
        con.commit()
    except sqlite3.Error as error:
        print("Error while deleting Location table from sqlite", error)
    finally:
        if con:
            con.close()
    print("...done.")

def create_tables(database_path):
    create_queries = [
        ("Zone", zonerepo.queries['create']),
        ("Synonym", synonymrepo.queries['create']),
        ("Event", eventrepo.queries['create']),
        ("Damage", damagerepo.queries['create']),
        ("Palm", palmrepo.queries['create']),
        ("PalmObservation", palmobservationrepo.queries['create']),
        ("Palm Synonym", palmsynonymrepo.queries['create']),
        ("Cycad", cycadrepo.queries['create']),
        ("Cycad Observation", cycadobservationrepo.queries['create']),
        ("Location", locationrepo.queries['create']),
        ("palm views", palmrepo.queries['create_views']),
    ]

    print("Creating tables...")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        for query in create_queries:
            print("\t" + query[0])
            cur.executescript(query[1])
            con.commit()
    except sqlite3.Error as error:
        print("Error while creating sqlite tables.", error)
    finally:
        if con:
            con.close()
    print("...done.")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare the database schema for importing from Excel."
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Specify the database full path. Default: palmhardiness.db",
        default="palmhardiness.db",
        required=False
    )
    parser.add_argument(
        "-d",
        "--drop",
        action="store_true",
        help="Drop all tables except Location then create all tables (including Location.) You will lose all existing data, except Location.",
        required=False
    )    
    parser.add_argument(
        "--location",
        action="store_true",
        help="Drop Location table. You will lose all existing location data. This option exists because repopulating Location requires time and a network connection.",
        required=False
    )

    args = parser.parse_args()
        
    if args.drop:
        drop_tables(args.path)
    if args.location:
        drop_location_table(args.path)

    create_tables(args.path)

if __name__ == "__main__":
    main()
