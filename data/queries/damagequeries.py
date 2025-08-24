queries = {
    "drop": """
DROP TABLE IF EXISTS "Damage"
    """,

    "create": """
CREATE TABLE IF NOT EXISTS "Damage" (
    "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    "LegacyId" integer,
    "Text" varchar(128) NOT NULL,
    "LastModified" timestamp NOT NULL,
    "WhoModified" varchar(128) NOT NULL
);
    """,

    "insert": """
INSERT INTO Damage (Id, LegacyId, Text, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?)
    """,

    "select_by_legacy_id": """
SELECT Id
FROM Damage
WHERE LegacyId = ?
LIMIT 1
    """,

    "select_by_text": """
SELECT Id
FROM Damage
WHERE Text = ?
LIMIT 1
    """,
}