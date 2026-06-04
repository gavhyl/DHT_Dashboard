SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [AetnaQNXTRx].[etl].[tape] T (nolock)
JOIN [AetnaQNXTRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--where t.TableID in (1000,2000)
--WHERE f.[TableType] in ('COBC') and [FileName] like '%260408%'
ORDER BY TapeID desc