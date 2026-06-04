SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [ExcellusRx].[etl].[tape] T (nolock)
JOIN [ExcellusRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (1000,2000,4000,5500)
--WHERE F.TableName in ('TRR','DTL','PRM','SUP') and [FileName] like '%260423%'
--WHERE f.TableName like '%CAQH%' --Last Loaded: CAQH 4/28/26, Response 4/25/26, Bad Files 4/25/26
--WHERE FileName like '%ABII%'
ORDER BY TapeID desc