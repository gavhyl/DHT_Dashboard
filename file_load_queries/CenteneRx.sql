SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CenteneRx].[etl].[tape] T (nolock)
JOIN [CenteneRx].[config].[Table] F (nolock)
ON t.[TableID] = f.[TableID]
--WHERE t.[TableID] in (100,200,300)
--WHERE f.[TableName] in ('DTL','PRM','SUP') and [FileName] like '%260327%'
--WHERE t.[TableID] in (710) and [FileName] like '%260206%'
--WHERE f.[TableName] in ('TRR') and [FileName] like '%TRRD_260%'
ORDER BY [TapeID] desc