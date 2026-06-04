SELECT TOP 200 [TapeID], [ProdCtrlNo], [FileName], t.[TableID], f.[TableName], t.[ProcessStatus], [FileSize], [FileCreateDate], [FileLoadDate], [DataDescription]
FROM [HAPRx].[etl].[tape] T (nolock)
JOIN [HAPRx].[config].[Table] F (nolock)
ON t.TableID = f.TableID
--WHERE [FileName] like '%TPL%'
--WHERE f.[TableName] in ('DTL','PRM','SUP') --and [FileName] like '%260408%'
ORDER BY TapeID desc