queries = {
    "get_count": """
SELECT COUNT(*) as count
FROM (
        WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
        SELECT COUNT(*) as ObservationCount
        FROM Palm, vars
        LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
        LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
        -- Allow unobserved unless we are filtering them out
        WHERE (PalmObservation.Id IS NOT NULL OR filterObserved = 0)
        -- If there is a search term, then filter on it
            AND (term is NULL 
                OR INSTR(UPPER(Genus), term) > 0 
                OR INSTR(UPPER(Species), term) > 0 
                OR INSTR(UPPER(Variety), term) > 0 
                OR INSTR(UPPER(CommonName), term) > 0
                OR INSTR(UPPER(Zone.Name), term) > 0
    )
    GROUP BY Palm.Id
)
    """,

    "get_records": """
WITH vars AS (SELECT ? AS filterObserved, UPPER(?) AS term)
SELECT Palm.*
    ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, ''))  AS LongName
    ,Zone.Name as ZoneName
    ,COUNT(PalmObservation.Id) as ObservationCount
FROM Palm, vars
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
-- Allow unobserved unless we are filtering them out
WHERE (PalmObservation.Id IS NOT NULL OR filterObserved = 0)
-- If there is a search term, then filter on it
    AND (term is NULL 
        OR INSTR(UPPER(Genus), term) > 0 
        OR INSTR(UPPER(Species), term) > 0 
        OR INSTR(UPPER(Variety), term) > 0 
        OR INSTR(UPPER(CommonName), term) > 0
        OR INSTR(UPPER(Zone.Name), term) > 0
    )
GROUP BY Palm.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,


    "get_one": """
SELECT Palm.*
    ,TRIM(COALESCE(Palm.Genus, '') || ' ' || COALESCE(Palm.Species, '') || ' ' || COALESCE(Palm.Variety, '')) AS PalmName
    ,Zone.Name as ZoneName
	,(SELECT COUNT(*) 
		FROM PalmObservation
	WHERE PalmId = Palm.Id) AS [ObservationCount]
FROM Palm
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
WHERE Palm.Id = ?
    """,


    "drop": """
DROP TABLE IF EXISTS "Palm"
    """,


    "create": """
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
    """,

    "insert": """
INSERT INTO Palm (Id, LegacyId, Genus, Species, Variety, CommonName, ZoneId, LastModified, WhoModified) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    "select_by_legacy_id": """
SELECT Id
FROM Palm
WHERE LegacyId = ?
LIMIT 1
    """,

    "get_all_with_palmobservation_count": """
SELECT Palm.*
    ,Zone.Name as ZoneName
    ,COUNT(PalmObservation.Id) as ObservationCount
FROM Palm
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN PalmObservation ON Palm.Id = PalmObservation.PalmId
GROUP BY Palm.Id
ORDER BY Genus, Species, Variety
LIMIT ? OFFSET ?
    """,

    "get_observations_for_palm": """
SELECT PalmObservation.LegacyId
	,PalmObservation.LastModified
	,PalmObservation.WhoModified
	,PalmObservation.WhoReported
	,PalmObservation.LowTemp
    ,TRIM(COALESCE(Palm.Genus, '') || ' ' || COALESCE(Palm.Species, '') || ' ' || COALESCE(Palm.Variety, '')) AS PalmName
    ,Palm.LegacyId as PalmLegacyId
    ,Palm.Genus as PalmGenus
    ,Palm.Species as PalmSpecies
    ,Palm.Variety as PalmVariety
    ,Palm.CommonName as PalmCommonName
    ,Palm.ZoneId as PalmZoneId
    ,Zone.Name as ZoneName
    ,Location.City as LocationCity
    ,Location.State as LocationState
    ,Location.Country as LocationCountry
    ,Location.Latitude AS LocationLatitude
    ,Location.Longitude AS LocationLongitude
	,TRIM(COALESCE(Location.City, '') || ', ' || COALESCE(Location.State, '') || ', ' || COALESCE(Location.Country, ''), ', ') AS LocationName
FROM PalmObservation
LEFT JOIN Palm ON PalmObservation.PalmId = Palm.Id
LEFT JOIN Zone ON Palm.ZoneId = Zone.Id
LEFT JOIN Location ON PalmObservation.LocationId = Location.Id
WHERE PalmObservation.PalmId = ?
ORDER BY PalmObservation.LowTemp DESC
    """,

  "get_count_lowest_surviving_for_all_palms": """
SELECT COUNT(*)
FROM (
  WITH vars AS (SELECT UPPER(?) AS term)
  SELECT 
    P.Id
    ,P.Genus
    ,P.Species
  FROM PalmObservation AS O, vars
    INNER JOIN Palm AS P ON O.PalmId = P.Id
    INNER JOIN Damage AS D ON O.DamageId = D.Id
  WHERE UPPER(D.Text) NOT LIKE 'DEATH'
    AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION%'
    AND (term is NULL 
        OR INSTR(UPPER(Genus), term) > 0 
        OR INSTR(UPPER(Species), term) > 0)
  GROUP BY Genus, Species
)
""",

  "get_lowest_surviving_for_all_palms": """
WITH vars AS (SELECT UPPER(?) AS term)
SELECT 
  P.Id
  ,D.Text
  ,P.Genus
  ,P.Species
  ,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '')) AS PalmName
  ,MIN(O.LowTemp) AS [Min]
  ,MAX(O.LowTemp) AS [Max]
  ,ROUND(AVG(O.LowTemp), 2) AS [Average]
  ,COUNT(*) AS [Records]
FROM PalmObservation AS O, vars
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND (term is NULL 
      OR INSTR(UPPER(Genus), term) > 0 
      OR INSTR(UPPER(Species), term) > 0)
GROUP BY Genus, Species
ORDER BY  Genus ASC, Species ASC, [Min] ASC
LIMIT ? OFFSET ?
    """,

    "get_stat_LOWESTSURVIVED": """
SELECT MIN(o.LowTemp) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
INNER JOIN Damage AS d ON o.DamageId = d.Id
WHERE p.Id = ?
    AND (UPPER(d.Text) NOT LIKE 'DEATH' AND UPPER(d.Text) NOT LIKE 'NO CONFIRMATION')
    """,

    "get_stat_NUMOBSERVATIONS": """
SELECT COUNT(*) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
WHERE p.Id = ?
    """,

    "get_stat_NUMEVENTS": """
SELECT COUNT(event) AS [value]
FROM (
    SELECT DISTINCT(e.Id) AS [event]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
    GROUP BY e.Id
)
    """,

    "get_stat_MOSTREPORTEDBY": """
SELECT [who] AS [value]
FROM (
    SELECT 
		e.WhoReported AS [who]
		,COUNT(e.WhoReported) AS [count]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
    GROUP BY e.WhoReported
)
ORDER BY [count] DESC
LIMIT 1
    """,

    "get_stat_MOSTCOMMONLOCATION": """
SELECT [location] AS [value]
	,COUNT(*) AS [count]
FROM (
    SELECT 
		o.City || COALESCE(', ' || o.State, '') || COALESCE(', ' || o.Country, '') AS [location]
    FROM PalmObservation AS o
    INNER JOIN Palm AS p ON o.PalmId = p.Id
    INNER JOIN Event AS e ON o.EventId = e.Id
    WHERE p.Id = ?
)
GROUP BY [location]
ORDER BY [count] DESC
LIMIT 1
    """,
}