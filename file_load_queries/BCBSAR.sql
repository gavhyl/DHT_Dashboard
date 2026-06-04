SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [BCBSAR].[etl].[tape] T (nolock)
JOIN [BCBSAR].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc