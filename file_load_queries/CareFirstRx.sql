SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CareFirstRx].[etl].[tape] T (nolock)
JOIN [CareFirstRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE f.[TableID] in (1000,2000,3000,4000,5500,5600)
--WHERE f.[TableName] in ('TRR','DTL','PRM','SUP') and [FileName] like '%260%'
--where [FileName] like '%ABII%'
ORDER BY TapeID desc