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
        ("Zone", zonerepo.queries['create']),
        ("Synonym", synonymrepo.queries['create']),
        ("Event", eventrepo.queries['create']),
        ("Damage", damagerepo.queries['create']),
        ("Palm", palmrepo.queries['create']),
        ("PalmObservation", palmobservationrepo.queries['create']),
        ("Palm Synonym", palmsynonymrepo.queries['create']),
        ("Cycad", cycadrepo.queries['create']),
        ("Cycad Observation", cycadobservationrepo.queries['create']),
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
