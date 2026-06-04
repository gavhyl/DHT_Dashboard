SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [CignaRx].[etl].[tape] T (nolock)
JOIN [CignaRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (1000,2000,5600,5700,7000)
--WHERE F.TableName in ('TRR','DTL','PRM','SUP') and [FileName] like '%260422%'
--WHERE [FileName] like '%ABII%'
ORDER BY TapeID desc