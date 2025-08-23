queries = {
    "drop": """
DROP TABLE IF EXISTS "CycadObservation"
    """,
    
    "create": """
CREATE TABLE IF NOT EXISTS "CycadObservation" (
    "Id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    "LastModified" timestamp NOT NULL,
    "WhoModified" varchar(128) NOT NULL,
    "CycadId" integer NOT NULL,
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
    FOREIGN KEY (CycadId) REFERENCES "Cycad" (Id),
    FOREIGN KEY (DamageId) REFERENCES "Damage" (Id),
    FOREIGN KEY (EventId) REFERENCES "Event" (Id),
    FOREIGN KEY (LocationId) REFERENCES "Location" (Id)
);
    """,

        "get_all_for_cycad": """
SELECT CycadObservation.*
    ,Event.Name as EventName
    ,Event.Description as EventDescription
    ,Event.WhoReported as EventWhoReported
    ,Damage.Text as DamageText
    --,Location.City as LocationCity
    --,Location.State as LocationState
    --,Location.Country as LocationCountry
    --,Location.Id as LocationId
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
FROM CycadObservation
LEFT JOIN Event on CycadObservation.EventId = Event.Id
LEFT JOIN Damage on CycadObservation.DamageId = Damage.Id
LEFT JOIN Location on CycadObservation.LocationId = Location.Id
WHERE CycadId = ?
    """,


    "get_all_count": """
SELECT COUNT(*) FROM [CycadObservation]
    """,

    "get_all": """
SELECT 
    CycadObservation.Id
    ,CycadObservation.CycadId
    ,CycadObservation.Description
    ,Damage.Text AS DamageText
    ,CycadObservation.LowTemp
    ,CycadObservation.EventId
    ,CycadObservation.LastModified
    ,CycadObservation.WhoModified
    ,CycadObservation.WhoReported
    ,CycadObservation.Source
    --,Cycad.Genus AS Genus
    --,Cycad.Species AS Species
    ,Cycad.Id AS CycadId
    ,Cycad.CommonName AS CommonName
    ,Cycad.Variety AS Variety
    ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, ''))  AS Name
    ,Event.Name AS EventName
    --,Location.Id AS LocationId
    --,Location.City AS City
    --,Location.State AS State
    --,Location.Country AS Country
    ,Location.Latitude AS Latitude
    ,Location.Longitude AS Longitude
    --,Location.Geo AS Geo
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
    ,'CycadObservation' AS [Type]
FROM CycadObservation
LEFT JOIN Cycad ON CycadObservation.CycadId = Cycad.Id
LEFT JOIN Event ON CycadObservation.EventId = Event.Id
LEFT JOIN Damage ON CycadObservation.DamageId = Damage.Id
LEFT JOIN Location ON CycadObservation.LocationId = Location.Id
    """,
}