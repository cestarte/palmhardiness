import sqlite3
import argparse
from data.repositories import zone
from data.repositories import damage
from data.repositories import synonym
from data.repositories import event
from data.repositories import palm
from data.repositories import palmsynonym
from data.repositories import palmobservation
from data.repositories import cycad
from data.repositories import cycadobservation

def drop_tables(database_path):
    drop_queries = [
        ("Cycad Observation", cycadobservation.queries['drop']),
        ("Cycad", cycad.queries['drop']),
        ("Palm Synonym", palmsynonym.queries['drop']),
        ("PalmObservation", palmobservation.queries['drop']),
        ("Palm", palm.queries['drop']),
        ("Damage", damage.queries['drop']),
        ("Event", event.queries['drop']),
        ("Synonym", synonym.queries['drop']),
        ("Zone", zone.queries['drop']),
    ]

    print("Dropping tables...")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        for query in drop_queries:
            print("\t" + query[0])
            cur.execute(query[1])
            con.commit()
    except sqlite3.Error as error:
        print("Error while deleting tables from sqlite", error)
    finally:
        if con:
            con.close()
    print("...done.")


def create_tables(database_path):
    create_queries = [
        ("Zone", zone.queries['create']),
        ("Synonym", synonym.queries['create']),
        ("Event", event.queries['create']),
        ("Damage", damage.queries['create']),
        ("Palm", palm.queries['create']),
        ("PalmObservation", palmobservation.queries['create']),
        ("Palm Synonym", palmsynonym.queries['create']),
        ("Cycad", cycad.queries['create']),
        ("Cycad Observation", cycadobservation.queries['create']),
    ]

    print("Creating tables...")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        for query in create_queries:
            print("\t" + query[0])
            cur.execute(query[1])
            con.commit()
    except sqlite3.Error as error:
        print("Error while creating sqlite tables.", error)
    finally:
        if con:
            con.close()
    print("...done.")


def main():
    database_path = "palmhardiness.db"
    parser = argparse.ArgumentParser(
        description="Prepare the database schema for importing from Excel."
    )
    parser.add_argument(
        "-d",
        "--drop",
        action="store_true",
        help="If specified, will drop tables before creating. You will lose all existing data.",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Specify the database full path. Default: palmhardiness.db",
    )

    args = parser.parse_args()
    print(args)
    if args.path:
        database_path = args.path
        
    if args.drop:
        drop_tables(database_path)

    create_tables(database_path)

if __name__ == "__main__":
    main()
