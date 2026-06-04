SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [EmblemRx].[etl].[tape] T (nolock)
JOIN [EmblemRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (1000,2000,3000)
--WHERE f.[TableName] in ('Group') and [FileName] like '%20260430%'
--WHERE f.[TableName] in ('DTL', 'PRM', 'SUP') and [FileName] like '%260423%'
ORDER BY TapeID desc


--EmblemRx is migrating PBMs from ESI to Prime, moved on 1/1/26. Migration/new implementation is TBD.