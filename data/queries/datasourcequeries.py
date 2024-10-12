
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
