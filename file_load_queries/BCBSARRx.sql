SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [BCBSARRx].[etl].[tape] T (nolock)
JOIN [BCBSARRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.[TableID] in (1000,2000,5500,5600,5700)
--WHERE t.[TableID] in (5000,5100,5200,5400) and [FileName] like '%260422%'
--WHERE t.[TableID] in (5700)
ORDER BY TapeID desc

--select *
--from [BCBSARRx].[config].[Table]