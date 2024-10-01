

import openpyxl
import sqlite3
from util.string import clean
from data.models.lowestsurviving import LowestSurviving

queries = {
  "get_count_lowest_surviving_for_all_palms": """
SELECT COUNT(*)
FROM (
  WITH vars AS (SELECT UPPER(?) AS term)
  SELECT 
    P.Id
    ,P.Genus
    ,P.Species
    ,MIN(O.LowTemp) AS [Min]
    ,MAX(O.LowTemp) AS [Max]
    ,ROUND(AVG(O.LowTemp), 2) AS [Average]
    ,COUNT(*) AS [Records]
  FROM PalmObservation AS O, vars
    INNER JOIN Palm AS P ON O.PalmId = P.Id
    INNER JOIN Damage AS D ON O.DamageId = D.Id
  WHERE UPPER(D.Text) NOT LIKE 'DEATH'
    AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION%'
    AND (term is NULL 
        OR INSTR(UPPER(Genus), term) > 0 
        OR INSTR(UPPER(Species), term) > 0)
  GROUP BY Genus, Species
  ORDER BY  Genus ASC, Species ASC, Min ASC
)
""",

  "get_lowest_surviving_for_all_palms": """
WITH vars AS (SELECT UPPER(?) AS term)
SELECT 
  P.Id
  ,P.Genus
  ,P.Species
  ,MIN(O.LowTemp) AS [Min]
  ,MAX(O.LowTemp) AS [Max]
  ,ROUND(AVG(O.LowTemp), 2) AS [Average]
  ,COUNT(*) AS [Records]
FROM PalmObservation AS O, vars
  INNER JOIN Palm AS P ON O.PalmId = P.Id
  INNER JOIN Damage AS D ON O.DamageId = D.Id
WHERE UPPER(D.Text) NOT LIKE 'DEATH'
  AND UPPER(D.Text) NOT LIKE 'NO CONFIRMATION%'
  AND (term is NULL 
      OR INSTR(UPPER(Genus), term) > 0 
      OR INSTR(UPPER(Species), term) > 0)
GROUP BY Genus, Species
ORDER BY  Genus ASC, Species ASC, Min ASC
LIMIT ? OFFSET ?
    """,
}


def read_lowest_surviving_from_row(row:sqlite3.Row) -> LowestSurviving:
    o = LowestSurviving()
    o.id = row['Id']
    o.genus = row['Genus']
    o.species = row['Species']
    o.min = row['Min']
    o.max = row['Max']
    o.average = row['Average']
    o.records = row['Records']

    return o

