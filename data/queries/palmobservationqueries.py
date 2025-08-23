queries = {
    "drop": """
DROP TABLE IF EXISTS "PalmObservation"
    """,

    "create": """
CREATE TABLE IF NOT EXISTS "PalmObservation" (
    "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    "LastModified" timestamp NOT NULL,
    "WhoModified" varchar(128) NOT NULL,
    "PalmId" integer NOT NULL,
    "WhoReported" varchar(512) NOT NULL,
    "City" varchar(512) NOT NULL,
    "State" varchar(512),
    "Country" varchar NOT NULL,
    "LowTemp" real NOT NULL,
    "DamageId" integer NOT NULL,
    "Description" varchar,
    "Source" varchar,
    "EventId" integer,
    "EventLegacyId" integer,
    "LocationId" integer,
    FOREIGN KEY (PalmId) REFERENCES "Palm" (Id),
    FOREIGN KEY (DamageId) REFERENCES "Damage" (Id),
    FOREIGN KEY (EventId) REFERENCES "Event" (Id),
    FOREIGN KEY (LocationId) REFERENCES "Location" (Id)
);
    """,

    "insert": """
INSERT INTO PalmObservation (PalmId, WhoReported, City, State, Country, DamageId, EventId, EventLegacyId, Description, Source, LowTemp, LastModified, WhoModified) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,

    "get_all_for_palm": """
SELECT PalmObservation.*
    ,Event.Name as EventName
    ,Event.Description as EventDescription
    ,Event.Id AS EventId
    ,Damage.Text as DamageText
    ,Location.City as LocationCity
    ,Location.State as LocationState
    ,Location.Country as LocationCountry
    ,Location.Id as LocationId
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
FROM PalmObservation
LEFT JOIN Event on PalmObservation.EventId = Event.Id
LEFT JOIN Damage on PalmObservation.DamageId = Damage.Id
LEFT JOIN Location on PalmObservation.LocationId = Location.Id
WHERE PalmId = ?
    """,

    "get_all_count": """
SELECT COUNT(*) FROM [PalmObservation]
    """,

    "get_all": """
SELECT 
    PalmObservation.Id
    ,PalmObservation.PalmId
    ,PalmObservation.Description
    ,Damage.Text AS DamageText
    ,PalmObservation.LowTemp
    ,PalmObservation.EventId
    ,PalmObservation.LastModified
    ,PalmObservation.WhoModified
    ,PalmObservation.WhoReported
    ,PalmObservation.Source
    ,Palm.Id AS PalmId
    --,Palm.Genus AS Genus
    --,Palm.Species AS Species
    ,Palm.CommonName AS CommonName
    --,Palm.Variety AS Variety
    ,TRIM(COALESCE(Palm.Genus, '') || ' ' || COALESCE(Palm.Species, '') || ' ' || COALESCE(Palm.Variety, '')) AS Name
    ,Event.Name AS EventName
    --,Location.Id AS LocationId
    --,Location.City AS City
    --,Location.State AS State
    --,Location.Country AS Country
    ,Location.Latitude AS Latitude
    ,Location.Longitude AS Longitude
    --,Location.Geo AS Geo
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
    ,'PalmObservation' AS [Type]
FROM PalmObservation
LEFT JOIN Palm ON PalmObservation.PalmId = Palm.Id
LEFT JOIN Event ON PalmObservation.EventId = Event.Id
LEFT JOIN Damage ON PalmObservation.DamageId = Damage.Id
LEFT JOIN Location ON PalmObservation.LocationId = Location.Id
    """,
}