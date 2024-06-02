import sqlite3
from data.models.datasource import DataSource

queries = {
    "get_all": """
SELECT 
	[Source]
	,SUM([Count]) AS [Count]
    ,[Type]
FROM (
    -- palm records with a URL
    SELECT 
	    SUBSTR(Source, INSTR(Source, '//')+2, INSTR(SUBSTR(Source, INSTR(Source, '//')+2), '/')-1) as [Source]
	    ,COUNT(*) as Count
        ,'Palm' as [Type]
	FROM PalmObservation
	WHERE Source IS NOT NULL
	    AND Source LIKE '%http%'
	GROUP BY [Source]

	UNION ALL

    -- palm records without a URL
	SELECT [Source]
		,COUNT(*) as [Count]
        ,'Palm' as [Type]
	FROM PalmObservation
	WHERE Source IS NOT NULL
		AND Source NOT LIKE '%http%'

	UNION ALL
	
    -- cycad records with a URL
	SELECT
	    SUBSTR(Source, INSTR(Source, '//')+2, INSTR(SUBSTR(Source, INSTR(Source, '//')+2), '/')-1) as [Source]
	    ,COUNT(*) as Count
        ,'Cycad' as [Type]
	FROM CycadObservation
	WHERE Source IS NOT NULL
	    AND Source LIKE '%http%'
	GROUP BY [Source]

	UNION ALL

    -- cycad records without a URL
	SELECT [Source]
		,COUNT(*) as [Count]
        ,'Cycad' as [Type]
	FROM CycadObservation
	WHERE Source IS NOT NULL
		AND Source NOT LIKE '%http%'
)
GROUP BY [Source], [Type]
ORDER BY [Type], [Count] DESC
""",

}



def read_from_row(row:sqlite3.Row) -> DataSource:
    item = DataSource()
    item.source = row["Source"]
    item.count = row["Count"]
    item.type = row["Type"]
    return item
