SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [EverNorthRx].[etl].[tape] T (nolock)
JOIN [EverNorthRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE f.[TableID] in (1000)
ORDER BY TapeID desc