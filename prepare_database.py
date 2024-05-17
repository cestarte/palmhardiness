import sqlite3
import argparse


def drop_tables(databasePath):
    drop_zone_query = """
    DROP TABLE IF EXISTS "Zone"
    """

    drop_synonym_query = """
    DROP TABLE IF EXISTS "Synonym"
    """

    drop_event_query = """
    DROP TABLE IF EXISTS "Event"
    """

    drop_damage_query = """
    DROP TABLE IF EXISTS "Damage"
    """

    drop_cycad_query = """
    DROP TABLE IF EXISTS "Cycad"
    """

    drop_palm_query = """
    DROP TABLE IF EXISTS "Palm"
    """

    drop_palm_observation_query = """
    DROP TABLE IF EXISTS "PalmObservation"
    """
    drop_palm_synonym_query = """
    DROP TABLE IF EXISTS "PalmSynonym"
    """

    drop_cycad_observation_query = """
    DROP TABLE IF EXISTS "CycadObservation"
    """

    drop_queries = [
        ("Cycad Observation", drop_cycad_observation_query),
        ("Cycad", drop_cycad_query),
        ("Palm Synonym", drop_palm_synonym_query),
        ("PalmObservation", drop_palm_observation_query),
        ("Palm", drop_palm_query),
        ("Damage", drop_damage_query),
        ("Event", drop_event_query),
        ("Synonym", drop_synonym_query),
        ("Zone", drop_zone_query),
    ]

    print("Dropping tables...")
    try:
        con = sqlite3.connect(databasePath)
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


def create_tables(databasePath):
    create_zone_query = """
CREATE TABLE IF NOT EXISTS "Zone" (
  "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  "Name" varchar(5) NOT NULL,
  "MinTempF" integer NOT NULL,
  "MaxTempF" integer NOT NULL,
  "LastModified" timestamp NOT NULL,
  "WhoModified" varchar(128) NOT NULL
);
    """

    create_synonym_query = """
    CREATE TABLE IF NOT EXISTS "Synonym" (
      "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
      "PalmLegacyId" integer,
      "LastModified" timestamp NOT NULL,
      "WhoModified" varchar(128) NOT NULL,
      "Genus" varchar(256),
      "Species" varchar(128),
      "Variety" varchar(128)
    );
    """

    create_event_query = """
    CREATE TABLE IF NOT EXISTS "Event" (
      "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
      "LegacyId" integer,
      "LastModified" timestamp NOT NULL,
      "WhoModified" varchar(128) NOT NULL,
      "WhoReported" varchar(265) NOT NULL,
      "City" varchar(512) NOT NULL,
      "State" varchar(512) NOT NULL,
      "Country" varchar(512) NOT NULL,
      "Name" varchar NOT NULL,
      "Description" varchar NOT NULL
    );
    """

    create_damage_query = """
    CREATE TABLE IF NOT EXISTS "Damage" (
      "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
      "LegacyId" integer,
      "Text" varchar(128) NOT NULL,
      "LastModified" timestamp NOT NULL,
      "WhoModified" varchar(128) NOT NULL
    );
    """

    create_cycad_query = """
    CREATE TABLE IF NOT EXISTS "Cycad" (
    "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    "LegacyId" integer,
    "Genus" varchar(512) NOT NULL,
    "Species" varchar(256),
    "Variety" varchar(256),
    "CommonName" varchar(256),
    "ZoneId" integer NOT NULL,
    "LastModified" timestamp NOT NULL,
    "WhoModified" varchar(128) NOT NULL,
    FOREIGN KEY (ZoneId) REFERENCES "Zone" (Id)
    );
    """

    create_palm_query = """
CREATE TABLE IF NOT EXISTS "Palm" (
  "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  "LegacyId" integer,
  "Genus" varchar(512) NOT NULL,
  "Species" varchar(256),
  "Variety" varchar(256),
  "CommonName" varchar(256),
  "ZoneId" integer NOT NULL,
  "LastModified" timestamp NOT NULL,
  "WhoModified" varchar(128) NOT NULL,
  FOREIGN KEY (ZoneId) REFERENCES "Zone" (Id)
);
    """

    create_palm_observation_query = """
    CREATE TABLE IF NOT EXISTS "PalmObservation" (
      "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
      "LegacyId" integer,
      "LastModified" timestamp NOT NULL,
      "WhoModified" varchar(128) NOT NULL,
      "PalmId" integer NOT NULL,
      "PalmLegacyId" integer NOT NULL,
      "WhoReported" varchar(512) NOT NULL,
      "City" varchar(512) NOT NULL,
      "State" varchar(512),
      "Country" varchar NOT NULL,
      "LowTemp" real NOT NULL,
      "DamageId" integer NOT NULL,
      "DamageLegacyId" integer NOT NULL,
      "Description" varchar,
      "Source" varchar,
      "EventId" integer,
      "EventLegacyId" integer,
      FOREIGN KEY (PalmId) REFERENCES "Palm" (Id),
      FOREIGN KEY (DamageId) REFERENCES "Damage" (Id),
      FOREIGN KEY (EventId) REFERENCES "Event" (Id)
    );
    """
    create_palm_synonym_query = """
    CREATE TABLE IF NOT EXISTS "PalmSynonym" (
      "PalmId" integer NOT NULL,
      "SynonymId" integer NOT NULL,
      FOREIGN KEY (PalmId) REFERENCES "Palm" (Id),
      FOREIGN KEY (SynonymId) REFERENCES "Synonym" (Id)
    );
    """

    create_cycad_observation_query = """
    CREATE TABLE IF NOT EXISTS "CycadObservation" (
      "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
      "LegacyId" integer,
      "LastModified" timestamp NOT NULL,
      "WhoModified" varchar(128) NOT NULL,
      "CycadId" integer NOT NULL,
      "CycadLegacyId" integer NOT NULL,
      "WhoReported" varchar(512) NOT NULL,
      "City" varchar(512) NOT NULL,
      "State" varchar(512),
      "Country" varchar NOT NULL,
      "LowTemp" real NOT NULL,
      "DamageId" integer NOT NULL,
      "DamageLegacyId" integer NOT NULL,
      "Description" varchar,
      "Source" varchar,
      "EventId" integer,
      "EventLegacyId" integer,
      FOREIGN KEY (CycadId) REFERENCES "Cycad" (Id),
      FOREIGN KEY (DamageId) REFERENCES "Damage" (Id),
      FOREIGN KEY (EventId) REFERENCES "Event" (Id)
    );
    """

    create_queries = [
        ("Zone", create_zone_query),
        ("Synonym", create_synonym_query),
        ("Event", create_event_query),
        ("Damage", create_damage_query),
        ("Palm", create_palm_query),
        ("PalmObservation", create_palm_observation_query),
        ("Palm Synonym", create_palm_synonym_query),
        ("Cycad", create_cycad_query),
        ("Cycad Observation", create_cycad_observation_query),
    ]

    print("Creating tables...")
    try:
        con = sqlite3.connect(databasePath)
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
    database_path = "PalmTalk.db"
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
        help="Specify the database full path. Default: PalmTalk.db",
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
