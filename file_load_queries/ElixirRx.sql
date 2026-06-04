SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], f.[TableType], [ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription] 
FROM [ElixirRx].[etl].[tape] T (nolock)
JOIN [ElixirRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE t.TableID in (1000,2000,4000)
--WHERE f.[TableName] in ('DTL','PRM','SUP') --and [FileName] like '%260316%'
--WHERE f.[TableName] in ('TRR') and [FileName] like '%D260401%'
Order by TapeID desc