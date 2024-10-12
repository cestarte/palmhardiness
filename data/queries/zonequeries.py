queries = {
    "drop": """
DROP TABLE IF EXISTS "Zone"
    """,

    "create": """
CREATE TABLE IF NOT EXISTS "Zone" (
  "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  "Name" varchar(5) NOT NULL,
  "MinTempF" integer NOT NULL,
  "MaxTempF" integer NOT NULL,
  "LastModified" timestamp NOT NULL,
  "WhoModified" varchar(128) NOT NULL
);
    """,

    "insert": """
INSERT INTO Zone (Id, Name, MinTempF, MaxTempF, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?)
    """,

    "select_by_name": """
SELECT Id
FROM Zone
WHERE Zone.Name = ?
LIMIT 1
    """,
}