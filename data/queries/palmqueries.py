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

    "drop_views": """
DROP VIEW IF EXISTS v_palm_lowestsurvivedtemps;
DROP VIEW IF EXISTS v_palm_highestkillingtemps;
DROP VIEW IF EXISTS v_palm_highestdamagingtemps;
DROP VIEW IF EXISTS v_palm_lowestundamagedtemps;
DROP VIEW IF EXISTS v_palm_survival30;
DROP VIEW IF EXISTS v_palm_survival25;
DROP VIEW IF EXISTS v_palm_survival20;
DROP VIEW IF EXISTS v_palm_survival15;
DROP VIEW IF EXISTS v_palm_survival10;
DROP VIEW IF EXISTS v_palm_survival5;
DROP VIEW IF EXISTS v_palm_temps;
    """,

    "create_views": """
CREATE VIEW v_palm_lowestsurvivedtemps AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,MIN(O.LowTemp) AS [LowestSurvivedTemp]
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
GROUP BY P.Id;

CREATE VIEW v_palm_highestkillingtemps AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,MAX(O.LowTemp) AS [HighestKillingTemp]
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) LIKE 'DEATH'
GROUP BY P.Id;

CREATE VIEW v_palm_highestdamagingtemps AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,MAX(O.LowTemp) AS [HighestDamagingTemp]
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
	AND (UPPER(D.Text) LIKE '%SPEAR PULL%' 
		OR UPPER(D.Text) LIKE '%LEAF DAMAGE%')
GROUP BY P.Id;

CREATE VIEW v_palm_lowestundamagedtemps AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,MIN(O.LowTemp) AS [LowestUndamagedTemp]
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) LIKE 'NO DAMAGE'
GROUP BY P.Id;

CREATE VIEW v_palm_survival30 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 30
GROUP BY P.Id;

CREATE VIEW v_palm_survival25 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 25
GROUP BY P.Id;

CREATE VIEW v_palm_survival20 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 20
GROUP BY P.Id;

CREATE VIEW v_palm_survival15 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 15
GROUP BY P.Id;

CREATE VIEW v_palm_survival10 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 10
GROUP BY P.Id;

CREATE VIEW v_palm_survival5 AS
SELECT 
  P.Id
  --,TRIM(COALESCE(Genus, '') || ' ' || COALESCE(Species, '') || ' ' || COALESCE(Variety, '')) AS LongName
  ,COUNT(*) AS [Count]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION'
  AND LowTemp+0 <= 5
GROUP BY P.Id;

CREATE VIEW v_palm_temps AS
SELECT
  p.Id
  ,TRIM(COALESCE(p.Genus, '') || ' ' || COALESCE(p.Species, '') || ' ' || COALESCE(p.Variety, '')) AS LongName
  ,p.CommonName
  ,z.Name AS ZoneName
  ,hdt.HighestDamagingTemp
  ,(CASE WHEN hdt.Count IS NULL THEN 0 ELSE hdt.Count END) AS [HighestDamagingTempCount]
  ,hkt.HighestKillingTemp
  ,(CASE WHEN hkt.Count IS NULL THEN 0 ELSE hkt.Count END) AS [HighestKillingTempCount]
  ,lst.LowestSurvivedTemp
  ,(CASE WHEN lst.Count IS NULL THEN 0 ELSE lst.Count END) AS [LowestSurvivedTempCount]
  ,lut.LowestUndamagedTemp
  ,(CASE WHEN lut.Count IS NULL THEN 0 ELSE lut.Count END) AS [LowestUndamagedTempCount]
  ,(CASE WHEN s30.Count IS NULL THEN 0 ELSE s30.Count END) AS [Survived30Count]
  ,(CASE WHEN s25.Count IS NULL THEN 0 ELSE s25.Count END) AS [Survived25Count]
  ,(CASE WHEN s20.Count IS NULL THEN 0 ELSE s20.Count END) AS [Survived20Count]
  ,(CASE WHEN s15.Count IS NULL THEN 0 ELSE s15.Count END) AS [Survived15Count]
  ,(CASE WHEN s10.Count IS NULL THEN 0 ELSE s10.Count END) AS [Survived10Count]
  ,(CASE WHEN s5.Count IS NULL THEN 0 ELSE s5.Count END) AS [Survived5Count]
  ,COUNT(po.Id) AS TotalObservations
FROM PalmObservation as po
LEFT JOIN v_palm_highestdamagingtemps AS hdt ON po.PalmId = hdt.Id
LEFT JOIN v_palm_highestkillingtemps AS hkt on po.PalmId = hkt.Id
LEFT JOIN v_palm_lowestsurvivedtemps AS lst on po.PalmId = lst.Id
LEFT JOIN v_palm_lowestundamagedtemps AS lut on po.PalmId = lut.Id
LEFT JOIN v_palm_survival30 AS s30 on po.PalmId = s30.Id
LEFT JOIN v_palm_survival25 AS s25 on po.PalmId = s25.Id
LEFT JOIN v_palm_survival20 AS s20 on po.PalmId = s20.Id
LEFT JOIN v_palm_survival15 AS s15 on po.PalmId = s15.Id
LEFT JOIN v_palm_survival10 AS s10 on po.PalmId = s10.Id
LEFT JOIN v_palm_survival5 AS s5 on po.PalmId = s5.Id
LEFT JOIN Palm AS p ON p.Id = po.PalmId
LEFT JOIN Zone AS z ON p.ZoneId = z.Id
GROUP BY p.Id;
    """,

    "get_count_temps": """
WITH vars AS (SELECT UPPER(?) AS term)
SELECT COUNT(*)
FROM v_palm_temps, vars
WHERE (term is NULL
    OR INSTR(UPPER(CommonName), term) > 0
    OR INSTR(UPPER(ZoneName), term) > 0
    OR INSTR(UPPER(LongName), term) > 0
)
    """,

    "get_temps": """
WITH vars AS (SELECT UPPER(?) AS term)
SELECT * 
FROM v_palm_temps, vars
WHERE (term is NULL
    OR INSTR(UPPER(CommonName), term) > 0
    OR INSTR(UPPER(ZoneName), term) > 0
    OR INSTR(UPPER(LongName), term) > 0
)
    """,

    "select_by_legacy_id": """
SELECT Id
FROM Palm
WHERE LegacyId = ?
LIMIT 1
    """,

# Query takes 3 parameters: genus, species, variety
  "select_by_genus_species_variety": """
SELECT Id
FROM Palm
WHERE Genus = ?1 
  AND (CASE WHEN ?2 = 'None' THEN Species IS NULL ELSE Species IS ?2 END)
  AND (CASE WHEN ?3 = 'None' THEN Variety IS NULL ELSE Variety IS ?3 END)
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

  "get_count_lowest_survived_for_all_palms": """
SELECT COUNT(*)
FROM (
WITH vars AS (SELECT UPPER(?) AS term)
SELECT v_palmlowestsurvivedtemps.*
FROM v_palmlowestsurvivedtemps, vars
WHERE (term is NULL 
      OR INSTR(UPPER(Name), term) > 0)
)
""",

  "get_lowest_survived_for_all_palms": """
WITH vars AS (SELECT UPPER(?) AS term)
SELECT v_palmlowestsurvivedtemps.*
FROM v_palmlowestsurvivedtemps, vars
WHERE (term is NULL 
      OR INSTR(UPPER(Name), term) > 0)
    """,

    "get_stat_lowest_survived": """
SELECT MIN(o.LowTemp) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
INNER JOIN Damage AS d ON o.DamageId = d.Id
WHERE p.Id = ?
    AND (UPPER(d.Text) NOT LIKE 'DEATH' AND UPPER(d.Text) NOT LIKE 'NO CONFIRMATION')
    """,

    "get_stat_num_observations": """
SELECT COUNT(*) AS [value]
FROM PalmObservation AS o
INNER JOIN Palm AS p ON o.PalmId = p.Id
WHERE p.Id = ?
    """,

    "get_stat_num_events": """
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

    "get_stat_most_reported_by": """
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

    "get_stat_most_common_location": """
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