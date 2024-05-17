-- ----------------------------------------------
-- Palm observation by temp, genus, species
-- ----------------------------------------------
SELECT 
	O.LowTemp
	,P.Genus
	,P.Species
	,P.Variety
	,Z.Name AS [USDA Zone]
	,D.Text AS [Result]
	,O.City
	,O.Country
	,O.State
	,E.Name AS [Event Name]
	,E.Description AS [Event Desc]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  LEFT JOIN [Zone] AS Z ON P.ZoneId = Z.Id
  LEFT JOIN Damage AS D ON O.DamageId = D.Id
  LEFT JOIN [Event] AS E ON O.EventId = E.Id
ORDER BY LowTemp ASC, Genus ASC, Species ASC, 
  Variety ASC, [Event Name] ASC

-- ----------------------------------------------
-- Lowest temp by genus,species without death
-- ----------------------------------------------
SELECT 
  P.Genus
  ,P.Species
  ,MIN(O.LowTemp) AS [Min]
FROM PalmObservation AS O
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
GROUP BY Genus, Species
ORDER BY Min ASC, Genus ASC, Species ASC

-- ----------------------------------------------
-- Palm observation where living by 
-- lowest temp & # records by genus/species
-- ----------------------------------------------
SELECT 
  P.Genus
  ,P.Species
  ,MIN(O.LowTemp) AS [Min]
  ,MAX(O.LowTemp) AS [Max]
  ,ROUND(AVG(O.LowTemp), 2) AS [Average]
  ,COUNT(*) AS [Records]
FROM PalmObservation AS O
	INNER JOIN Palm AS P ON O.PalmId = P.Id
	INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
	AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION%'
GROUP BY Genus, Species
ORDER BY  Genus ASC, Species ASC, Min ASC


-- ----------------------------------------------
-- Palm observation count by location, genus/species
-- ----------------------------------------------
SELECT 
  O.City
  ,O.State
  ,O.Country
  ,P.Genus
  ,P.Species
  ,COUNT(*) AS [Records]
FROM PalmObservation AS O
	INNER JOIN Palm AS P ON O.PalmId = P.Id
	INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
	AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION%'
GROUP BY City, [State], Country, Genus, Species
ORDER BY City ASC, [State] ASC, Country ASC, Genus ASC, Species ASC



-- ----------------------------------------------
-- Palm observation for specific genus
-- ----------------------------------------------
SELECT 
  O.LowTemp
  ,D.Text AS [Damage]
  --,P.Genus
  ,P.Species
  ,P.Variety
  ,O.City
  ,O.State
  ,O.Country
  ,E.Name
  ,E.Description
  ,O.Source
FROM PalmObservation AS O
	INNER JOIN Palm AS P ON O.PalmId = P.Id
	INNER JOIN Damage AS D ON O.DamageId = D.Id
  LEFT JOIN Event AS E ON E.Id = O.EventId
WHERE UPPER(Genus) = 'SABAL'
ORDER BY LowTemp ASC, Damage ASC, Species ASC

-- ----------------------------------------------
-- Palm observation for specific species
-- ----------------------------------------------
SELECT 
  O.LowTemp
  ,D.Text AS [Damage]
  --,P.Species
  --,P.Genus
  ,P.Variety
  ,O.City
  ,O.State
  ,O.Country
  ,E.Name AS [Event Name]
  ,E.Description [Event Description]
  ,O.Source
FROM PalmObservation AS O
	INNER JOIN Palm AS P ON O.PalmId = P.Id
	INNER JOIN Damage AS D ON O.DamageId = D.Id
  LEFT JOIN Event AS E ON E.Id = O.EventId
WHERE UPPER(Genus) = 'SABAL'
	AND UPPER(Species) = 'CAUSIARUM'
ORDER BY  Damage DESC, LowTemp ASC
