SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [MMOHRx].[etl].[tape] T (nolock)
JOIN [MMOHRx].[config].[Table] F (nolock)
ON t.[TableID] = f.[TableID]
--WHERE t.[TableID] in (1000,2000)
--WHERE f.[TableType] = 'COBC' and [FileName] like '%260412%'
ORDER BY TapeID desc