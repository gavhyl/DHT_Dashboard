SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [AetnaHRP].[etl].[tape] T (nolock)
JOIN [AetnaHRP].[config].[Table] F (nolock)
ON t.TableID = f.TableID
ORDER BY TapeID desc

--Expected Daily Files (1): Claims
--TRGETL2