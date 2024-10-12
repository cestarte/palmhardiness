queries = {
    "drop": """
DROP TABLE IF EXISTS "Location"
    """,

    "create": """
        CREATE TABLE IF NOT EXISTS "Location" (
        "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
        "LastModified" timestamp NOT NULL,
        "WhoModified" varchar(128) NOT NULL,
        "Latitude" varchar(6),
        "Longitude" varchar(6),
        "City" varchar(512),
        "State" varchar(512),
        "Country" varchar NOT NULL,
        "WhenAttemptedGeocode" timestamp
        );
    """,

    "insert": """
INSERT INTO Location (LastModified, WhoModified, Latitude, Longitude, City, State, Country) VALUES(?, ?, ?, ?, ?, ?, ?)
    """,

    "get_records": """
        WITH vars AS (SELECT UPPER(?) AS term)
        SELECT 
            Location.*
	        ,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
            ,(SELECT COUNT(PalmObservation.Id) FROM PalmObservation WHERE PalmObservation.LocationId = Location.Id) AS PalmObservations
            ,(SELECT COUNT(CycadObservation.Id) FROM CycadObservation WHERE CycadObservation.LocationId = Location.Id) AS CycadObservations
            ,(SELECT COUNT(Event.Id) FROM Event WHERE Event.LocationId = Location.Id) AS Events
        FROM Location, vars
        WHERE (vars.term IS NULL 
            OR INSTR(UPPER(Location.City), vars.term) > 0 
            OR INSTR(UPPER(Location.State), vars.term) > 0 
            OR INSTR(UPPER(Location.Country), vars.term) > 0
        )
        ORDER BY Location.Country, Location.State, Location.City
        LIMIT ? OFFSET ?
    """,

    "get_count": """
        WITH vars AS (SELECT UPPER(?) AS term)
        SELECT COUNT(*) FROM Location, vars
        WHERE (term IS NULL 
            OR INSTR(UPPER(City), term) > 0 
            OR INSTR(UPPER(State), term) > 0 
            OR INSTR(UPPER(Country), term) > 0
        )
    """,

    "get_locations_from_other_tables": """
SELECT [City], [State], [Country], [Id] AS [SourceId], 'event' AS [Source]
FROM Event 
UNION 
SELECT [City], [State], [Country], [Id] AS [SourceId], 'palm' AS [Source]
FROM PalmObservation 
UNION 
SELECT [City], [State], [Country], [Id] AS [SourceId], 'cycad' AS [Source]
FROM CycadObservation
    """,

    "select_by_country_state_city": """
SELECT * FROM Location WHERE Country IS ? AND State IS ? AND City IS ?
    """,
}