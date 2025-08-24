
queries = {
    "get_all": """
SELECT 
	[Source]
	,SUM([Count]) AS [Count]
    ,[Type]
FROM (
    -- palm records with a URL
    SELECT 
	    SUBSTR(Source, INSTR(Source, '//')+2, INSTR(SUBSTR(Source, INSTR(Source, '//')+2), '/')-1) AS [Source]
	    ,COUNT(*) AS [Count]
        ,'Palm' AS [Type]
	FROM PalmObservation
	WHERE Source IS NOT NULL
	    AND Source LIKE '%http%'
	GROUP BY [Source]

	UNION ALL

    -- palm records without a URL
	SELECT [Source]
		,COUNT(*) AS [Count]
        ,'Palm' AS [Type]
	FROM PalmObservation
	WHERE Source IS NOT NULL
		AND Source NOT LIKE '%http%'
	GROUP BY [Source]

	UNION ALL
	
    -- cycad records with a URL
	SELECT
	    SUBSTR(Source, INSTR(Source, '//')+2, INSTR(SUBSTR(Source, INSTR(Source, '//')+2), '/')-1) AS [Source]
	    ,COUNT(*) AS Count
        ,'Cycad' AS [Type]
	FROM CycadObservation
	WHERE Source IS NOT NULL
	    AND Source LIKE '%http%'
	GROUP BY [Source]

	UNION ALL

    -- cycad records without a URL
	SELECT [Source]
		,COUNT(*) AS [Count]
        ,'Cycad' AS [Type]
	FROM CycadObservation
	WHERE Source IS NOT NULL
		AND Source NOT LIKE '%http%'
	GROUP BY [Source]
)
GROUP BY [Source], [Type]
ORDER BY [Type], [Count] DESC
""",

	"get_contributors": """
SELECT 
	[WhoReported]
	,SUM([Count]) AS [Count]
FROM (
	SELECT 
		[WhoReported]
		,COUNT(*) AS [Count]
	FROM PalmObservation
	WHERE [WhoReported] IS NOT NULL
	GROUP BY [WhoReported]

	UNION ALL

	SELECT 
		[WhoReported]
		,COUNT(*) AS [Count]
	FROM CycadObservation
	WHERE [WhoReported] IS NOT NULL
	GROUP BY [WhoReported]
)
GROUP BY [WhoReported]
ORDER BY [Count] DESC
"""

}
