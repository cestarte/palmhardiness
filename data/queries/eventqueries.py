queries = {
    "drop": """
DROP TABLE IF EXISTS "Event"
    """,

    "create": """
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
    "Description" varchar NOT NULL,
    "LocationId" integer,
    FOREIGN KEY (LocationId) REFERENCES "Location" (Id)
);
    """,

    "insert": """
INSERT INTO Event (Id, LegacyId, WhoReported, City, State, Country, Name, Description, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    "select_by_legacy_id": """
SELECT Id
FROM Event
WHERE LegacyId = ?
LIMIT 1
        """,

    "get_all_count": """
    SELECT COUNT(*) FROM [Event]
    """,

    "get_all": """
    SELECT Event.Id
        ,Event.LastModified
        ,Event.WhoModified
        ,Event.WhoReported
        ,Event.Name
        ,Event.Description
        --,Location.Id AS LocationId
        --,Location.City AS City
        --,Location.State AS State
        --,Location.Country AS Country
        ,Location.Latitude AS Latitude
        ,Location.Longitude AS Longitude
        --,Location.Geo AS Geo
        ,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
    FROM [Event], [Location] 
    WHERE [Event].LocationId = [Location].Id
    """,
}