queries = {
    "drop": """
DROP TABLE IF EXISTS "Synonym"
    """,
    "create": """
CREATE TABLE IF NOT EXISTS "Synonym" (
    "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    "PalmLegacyId" integer,
    "LastModified" timestamp NOT NULL,
    "WhoModified" varchar(128) NOT NULL,
    "Genus" varchar(256),
    "Species" varchar(128),
    "Variety" varchar(128)
);
    """,

    "insert": """
    INSERT INTO Synonym (Id, PalmLegacyId, Genus, Species, Variety, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?)
    """,
}