SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CenteneFidelisRx].[etl].[tape] T (nolock)
JOIN [CenteneFidelisRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (2000)
--WHERE f.[TableType] = 'COBC'
ORDER BY TapeID desc