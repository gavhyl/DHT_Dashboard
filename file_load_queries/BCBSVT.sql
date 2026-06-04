SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [BCBSVT].[etl].[tape] T (nolock)
JOIN [BCBSVT].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc