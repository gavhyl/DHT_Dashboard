SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [ElevanceMMMRx].[etl].[tape] T (nolock)
JOIN [ElevanceMMMRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.[TableID] in (1000,2000,5600)
--WHERE t.[TableID] in (5000,5100,5200) and [FileName] like '%260408%'
--WHERE t.[TableID] in (5600)
ORDER BY TapeID desc

--select *
--from [ElevanceMMMRx].[config].[Table]