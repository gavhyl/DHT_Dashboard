SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [PremeraMedAdvRx].[etl].[tape] T (nolock)
JOIN [PremeraMedAdvRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc